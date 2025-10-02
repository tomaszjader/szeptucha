import pyaudio
import keyboard
import threading
import time
import pyperclip
import win32gui
import win32con
from pynput import keyboard as pynput_keyboard
import sys
import os
import wave
import tempfile
from openai import OpenAI
import io
from dotenv import load_dotenv
import math
import numpy as np
import tkinter as tk

import queue
from collections import deque

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

class RecordingWindow:
    def __init__(self, root: tk.Tk):
        # Główny root Tk musi działać w głównym wątku
        self.root = root
        self.window = None
        self.canvas = None
        self.visible = False
        self.animation_frame = 0
        self.audio_level = 0.0  # Poziom dźwięku (0.0 - 1.0)
        self.audio_history = deque(maxlen=50)  # Historia poziomów dźwięku
        self.width, self.height = 300, 120

        # Kolejka do komunikacji między wątkami (show/hide z innych wątków)
        self.command_queue = queue.Queue()
        # Blokada dla bezpiecznego dostępu do danych audio
        self.data_lock = threading.Lock()

    def start(self):
        """Uruchamia pętlę przetwarzania poleceń i animacji (wątku głównego Tk)."""
        def tick():
            # Przetwórz oczekujące polecenia (show/hide) z innych wątków
            try:
                while True:
                    cmd = self.command_queue.get_nowait()
                    if cmd == 'show':
                        self._open_window()
                    elif cmd == 'hide':
                        self._close_window()
            except queue.Empty:
                pass

            # Aktualizuj animację jeśli okno widoczne
            if self.visible and self.canvas:
                try:
                    self._draw_wave_visualization(self.width, self.height)
                    self.animation_frame += 1
                except Exception:
                    # Cicha obsługa błędów rysowania
                    pass

            # Harmonogram kolejnego odświeżenia
            self.root.after(25, tick)

        # Uruchom pierwsze wywołanie tick
        self.root.after(25, tick)

    def show(self):
        """Żąda wyświetlenia okna (bezpośrednie wywołanie z dowolnego wątku)."""
        # Resetuj stan animacji
        self.animation_frame = 0
        with self.data_lock:
            self.audio_level = 0.0
            self.audio_history.clear()
        # Wyślij polecenie do kolejki
        self.command_queue.put('show')

    def hide(self):
        """Żąda ukrycia okna (bezpośrednie wywołanie z dowolnego wątku)."""
        self.command_queue.put('hide')

    def _open_window(self):
        if self.visible and self.window:
            return
        # Utwórz osobne okno jako Toplevel
        self.window = tk.Toplevel(self.root)
        self.window.title("🎤 Nagrywanie...")
        # Wyśrodkuj okno na ekranie
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
        # Zawsze na wierzchu
        try:
            self.window.attributes('-topmost', True)
        except Exception:
            pass

        # Canvas do rysowania
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack()

        # Obsługa zamknięcia
        def on_close():
            self.hide()
        self.window.protocol("WM_DELETE_WINDOW", on_close)

        self.visible = True

    def _close_window(self):
        if not self.visible:
            return
        try:
            if self.window:
                self.window.destroy()
        except Exception:
            pass
        finally:
            self.window = None
            self.canvas = None
            self.visible = False
    
    def _draw_wave_visualization(self, width, height):
        """Rysuje wizualizację fali dźwiękowej (Tkinter Canvas)"""
        # Wyczyść canvas
        if not self.canvas:
            return
        self.canvas.delete("all")

        # Tło i tekst
        self.canvas.create_rectangle(0, 0, width, height, fill="#1e1e1e", outline="")
        self.canvas.create_text(width // 2, 20, text="🎤 Nagrywanie...", fill="#ffffff", font=("Segoe UI", 12))

        # Parametry fali
        wave_area_height = 60
        wave_y_start = 40
        center_y = wave_y_start + wave_area_height // 2

        # Użyj poziomu dźwięku do kontroli amplitudy fali
        base_amplitude = 8 + (self.audio_level * 25)  # Amplituda od 8 do 33

        # Główna fala reagująca na dźwięk
        points = []
        for x in range(0, width, 3):
            base_wave = math.sin((x + self.animation_frame * 4) * 0.08)
            audio_influence = self.audio_level * math.sin((x + self.animation_frame * 6) * 0.12)
            wave_height = base_amplitude * (base_wave * 0.7 + audio_influence * 0.8)
            y = center_y + wave_height
            points.append((x, int(y)))

        def rgb_to_hex(r, g, b):
            return f"#{r:02x}{g:02x}{b:02x}"

        if len(points) >= 2:
            if self.audio_level < 0.3:
                intensity = int(100 + 155 * (self.audio_level / 0.3))
                color = (intensity//3, intensity//2, intensity)
            elif self.audio_level < 0.7:
                progress = (self.audio_level - 0.3) / 0.4
                blue = int(255 * (1 - progress))
                green = 255
                red = int(100 * progress)
                color = (red, green, blue)
            else:
                progress = (self.audio_level - 0.7) / 0.3
                red = int(100 + 155 * progress)
                green = 255
                blue = int(50 * (1 - progress))
                color = (red, green, blue)

            # Rysuj główną falę
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill=rgb_to_hex(*color), width=3)

        # Dodatkowe fale z historii
        if len(self.audio_history) > 5:
            for i in range(min(3, len(self.audio_history) // 8)):
                points2 = []
                history_index = -(i + 1) * 8
                if abs(history_index) <= len(self.audio_history):
                    historical_level = self.audio_history[history_index]
                    amplitude = 4 + (historical_level * 15)
                    for x in range(0, width, 6):
                        wave_height = amplitude * math.sin((x + self.animation_frame * 2 + i * 45) * 0.06)
                        y = center_y + wave_height
                        points2.append((x, int(y)))
                    if len(points2) >= 2:
                        alpha = 0.6 - (i * 0.15)
                        base_intensity = int(150 * alpha * (0.4 + historical_level * 0.6))
                        if historical_level < 0.5:
                            color2 = (base_intensity//4, base_intensity//2, base_intensity)
                        else:
                            color2 = (base_intensity//2, base_intensity, base_intensity//3)
                        for j in range(len(points2) - 1):
                            x1, y1 = points2[j]
                            x2, y2 = points2[j+1]
                            self.canvas.create_line(x1, y1, x2, y2, fill=rgb_to_hex(*color2), width=2)

        # Linie poziome dla efektu
        for i in range(3):
            y_pos = center_y + (i - 1) * 15
            opacity = int(40 + 30 * self.audio_level)
            line_color = (opacity//2, opacity, opacity//2)
            self.canvas.create_line(20, y_pos, width-20, y_pos, fill=rgb_to_hex(*line_color), width=1)
    
    def update_audio_level(self, audio_data):
        """Aktualizuje poziom dźwięku na podstawie danych audio"""
        with self.data_lock:
            try:
                # Konwertuj dane audio na numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                # Oblicz RMS (Root Mean Square) jako miarę głośności
                rms = np.sqrt(np.mean(audio_array**2))
                
                # Normalizuj do zakresu 0.0 - 1.0 i wygładź
                normalized_level = min(rms / 32767.0, 1.0)
                self.audio_level = (self.audio_level * 0.7) + (normalized_level * 0.3)
                
                # Dodaj do historii
                self.audio_history.append(self.audio_level)
                    
            except Exception as e:
                # W przypadku błędu, ustaw poziom na 0 (bez wypisywania błędu)
                self.audio_level = 0.0
    
    def hide(self):
        """Wysyła polecenie ukrycia okna do kolejki bez blokowania (duplikat)."""
        # Ujednolicenie zachowania: nie sprawdzamy już atrybutu 'running'.
        # Polecenie zostanie przetworzone w głównym wątku Tk.
        self.command_queue.put('hide')
    
    def _safe_close(self):
        """Zachowane dla kompatybilności (nieużywane po przeniesieniu na Toplevel)."""
        self._close_window()

class VoiceNotes:
    def __init__(self, root: tk.Tk):
        # Inicjalizacja OpenAI klienta
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ BŁĄD: Nie znaleziono klucza API OpenAI!")
            print("Ustaw zmienną środowiskową OPENAI_API_KEY lub dodaj plik .env")
            sys.exit(1)
        
        self.client = OpenAI(api_key=api_key)
        
        # Konfiguracja audio
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.audio = pyaudio.PyAudio()
        
        self.is_recording = False
        self.recording_thread = None
        self.hotkey_listener = None
        self.frames = []
        self.last_toggle_ts = 0.0  # Debounce dla skrótu
        
        # Inicjalizacja okienka nagrywania (na głównym wątku Tk)
        self.recording_window = RecordingWindow(root)
        
        print("✅ OpenAI Whisper API skonfigurowane pomyślnie!")
        
    def start_recording(self):
        """Rozpoczyna nagrywanie dźwięku"""
        if self.is_recording:
            print("⚠️ Nagrywanie już trwa!")
            return
            
        # Upewnij się, że poprzedni wątek nagrywania został zakończony
        if self.recording_thread and self.recording_thread.is_alive():
            print("⚠️ Czekam na zakończenie poprzedniego nagrywania...")
            self.recording_thread.join(timeout=3)
            
        self.is_recording = True
        self.frames = []  # Wyczyść poprzednie dane audio
        print("\n🎤 NAGRYWANIE ROZPOCZĘTE - mów teraz...")
        print("Naciśnij ponownie Ctrl+Alt aby zatrzymać nagrywanie")
        
        # Pokaż okienko nagrywania
        self.recording_window.show()
        
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording(self):
        """Zatrzymuje nagrywanie dźwięku"""
        if not self.is_recording:
            print("⚠️ Nagrywanie nie jest aktywne!")
            return
            
        self.is_recording = False
        print("⏹️ NAGRYWANIE ZATRZYMANE - przetwarzanie...")
        
        # Ukryj okienko nagrywania
        self.recording_window.hide()
        
        # Poczekaj na zakończenie wątku nagrywania
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5)
            
        # Wyczyść referencję do wątku
        self.recording_thread = None
    
    def _record_audio(self):
        """Nagrywa dźwięk i konwertuje na tekst używając OpenAI Whisper"""
        try:
            # Rozpocznij nagrywanie
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            self.frames = []
            print("🎤 Nagrywanie w toku...")
            
            # Nagrywaj dopóki is_recording jest True
            while self.is_recording:
                data = stream.read(self.chunk)
                self.frames.append(data)
                
                # Przekaż dane audio do okienka dla wizualizacji
                self.recording_window.update_audio_level(data)
            
            stream.stop_stream()
            stream.close()
            
            if not self.frames:
                print("❌ Brak danych audio do przetworzenia")
                return
                
            print("🔄 Przetwarzanie audio przez OpenAI Whisper...")
            
            # Zapisz audio do tymczasowego pliku WAV
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                wf = wave.open(temp_file.name, 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
                wf.close()
                
                # Wyślij do OpenAI Whisper API
                try:
                    with open(temp_file.name, 'rb') as audio_file:
                        transcript = self.client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            language="pl"
                        )
                    
                    text = transcript.text
                    if text.strip():
                        self._process_recognized_text(text)
                    else:
                        print("❌ Nie rozpoznano żadnego tekstu")
                        
                except Exception as e:
                    print(f"❌ Błąd OpenAI API: {e}")
                finally:
                    # Usuń tymczasowy plik
                    try:
                        os.unlink(temp_file.name)
                    except:
                        pass
                        
        except Exception as e:
            print(f"❌ Błąd podczas nagrywania: {e}")
        finally:
            self.is_recording = False
            # Ukryj okienko nagrywania w przypadku błędu
            self.recording_window.hide()
    
    def _process_recognized_text(self, text):
        """Przetwarza rozpoznany tekst"""
        print(f"\n📝 ROZPOZNANY TEKST:")
        print(f"'{text}'")
        print("-" * 50)
        
        # Sprawdź czy jakieś okno jest aktywne i w trybie pisania
        active_window = win32gui.GetForegroundWindow()
        if active_window and self._is_text_input_active():
            print("✍️ Wykryto aktywne pole tekstowe - wklejam tekst...")
            # Kopiuj do schowka i wklej
            pyperclip.copy(text)
            time.sleep(0.1)  # Krótka pauza
            # Wklejanie w osobnym wątku, aby uniknąć blokowania
            def _paste_async():
                try:
                    controller = pynput_keyboard.Controller()
                    controller.press(pynput_keyboard.Key.ctrl)
                    controller.press('v')
                    controller.release('v')
                    controller.release(pynput_keyboard.Key.ctrl)
                except Exception:
                    # Fallback do biblioteki keyboard, jeśli dostępna
                    try:
                        import keyboard as kb
                        kb.send('ctrl+v')
                    except Exception:
                        pass
            threading.Thread(target=_paste_async, daemon=True).start()
        else:
            print("💬 Tekst wyświetlony w terminalu")
    
    def _is_text_input_active(self):
        """Sprawdza czy aktywne jest pole tekstowe"""
        try:
            # Pobierz informacje o aktywnym oknie
            hwnd = win32gui.GetForegroundWindow()
            class_name = win32gui.GetClassName(hwnd)
            window_text = win32gui.GetWindowText(hwnd)
            
            # Lista klas okien, które prawdopodobnie mają pola tekstowe
            text_input_classes = [
                'Edit', 'RichEdit', 'RichEdit20A', 'RichEdit20W',
                'Notepad', 'WordPadClass', 'OpusApp',  # Word
                'Chrome_WidgetWin_1', 'MozillaWindowClass',  # Przeglądarki
                'Vim', 'ConsoleWindowClass'  # Edytory tekstu
            ]
            
            # Sprawdź czy nazwa klasy sugeruje pole tekstowe
            for text_class in text_input_classes:
                if text_class.lower() in class_name.lower():
                    return True
            
            # Sprawdź czy tytuł okna sugeruje edytor tekstu
            text_indicators = ['notepad', 'word', 'editor', 'code', 'text']
            for indicator in text_indicators:
                if indicator.lower() in window_text.lower():
                    return True
                    
            return False
        except:
            return False
    
    def toggle_recording(self):
        """Przełącza stan nagrywania"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def setup_hotkey(self):
        """Konfiguruje globalny skrót klawiszowy Ctrl+Alt"""
        def on_hotkey():
            # Debounce, żeby uniknąć podwójnych wywołań
            now = time.time()
            if (now - self.last_toggle_ts) < 0.7:
                return
            self.last_toggle_ts = now
            self.toggle_recording()

        try:
            # Użyj pynput GlobalHotKeys dla Ctrl+Alt
            self.hotkey_listener = pynput_keyboard.GlobalHotKeys({
                '<ctrl>+<alt>': on_hotkey
            })
            self.hotkey_listener.start()
            print("🔥 Skrót klawiszowy Ctrl+Alt został aktywowany!")
            return True
        except Exception as e:
            print(f"❌ Błąd podczas konfiguracji skrótu klawiszowego: {e}")
            return False
    
    def run(self):
        """Uruchamia aplikację (nie blokuje wątku głównego Tk)."""
        print("=" * 60)
        print("🎙️  NOTATNIK GŁOSOWY - OpenAI Whisper")
        print("=" * 60)
        print("📋 Instrukcje:")
        print("• Naciśnij Ctrl+Alt aby rozpocząć/zatrzymać nagrywanie")
        print("• Mów wyraźnie po polsku")
        print("• Tekst zostanie wyświetlony w terminalu")
        print("• Jeśli aktywne jest pole tekstowe, tekst zostanie wklejony")
        print("• Naciśnij Ctrl+C aby zakończyć program")
        print("• Używa OpenAI Whisper API dla najlepszej jakości rozpoznawania")
        print("=" * 60)
        
        if not self.setup_hotkey():
            print("❌ Nie udało się skonfigurować skrótu klawiszowego")
            return
        # Uruchom pętlę animacji/komend okienka
        self.recording_window.start()
        print("✅ Aplikacja działa! Oczekiwanie na skrót klawiszowy...")

def main():
    """Funkcja główna"""
    # Główny root Tk musi być utworzony w głównym wątku
    root = tk.Tk()
    # Ukryj główne okno (używamy tylko Toplevel do nagrywania)
    try:
        root.withdraw()
    except Exception:
        pass

    try:
        app = VoiceNotes(root)
        app.run()
        # Pętla główna Tkinter (blokuje do zamknięcia)
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Zamykanie aplikacji...")
        if app.hotkey_listener:
            app.hotkey_listener.stop()
        if app.is_recording:
            app.stop_recording()
        app.recording_window.hide()
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        input("Naciśnij Enter aby zakończyć...")
    finally:
        # Zwolnij zasoby audio
        try:
            app.audio.terminate()
        except Exception:
            pass

if __name__ == "__main__":
    main()