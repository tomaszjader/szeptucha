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
import tkinter as tk
from tkinter import ttk
import math
import numpy as np

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

class RecordingWindow:
    def __init__(self):
        self.window = None
        self.canvas = None
        self.animation_running = False
        self.animation_frame = 0
        self.root = None
        self.audio_level = 0.0  # Poziom dźwięku (0.0 - 1.0)
        self.audio_history = []  # Historia poziomów dźwięku
        
    def show(self):
        """Pokazuje okienko nagrywania"""
        if self.window is not None:
            return
        
        # Utwórz root window jeśli nie istnieje
        if self.root is None:
            self.root = tk.Tk()
            self.root.withdraw()  # Ukryj główne okno
            
        self.window = tk.Toplevel(self.root)
        self.window.title("Nagrywanie...")
        self.window.geometry("200x80")
        self.window.resizable(False, False)
        
        # Ustaw okno zawsze na wierzchu
        self.window.attributes('-topmost', True)
        
        # Wyśrodkuj okno na ekranie
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (200 // 2)
        y = (self.window.winfo_screenheight() // 2) - (80 // 2)
        self.window.geometry(f"200x80+{x}+{y}")
        
        # Dodaj etykietę
        label = tk.Label(self.window, text="🎤 Nagrywanie...", font=("Arial", 12, "bold"))
        label.pack(pady=5)
        
        # Dodaj canvas dla animacji fali
        self.canvas = tk.Canvas(self.window, width=180, height=40, bg='white')
        self.canvas.pack(pady=5)
        
        # Rozpocznij animację
        self.animation_running = True
        self.animate_wave()
        
        # Zapobiegnij zamknięciu okna przez użytkownika
        self.window.protocol("WM_DELETE_WINDOW", lambda: None)
        
    def update_audio_level(self, audio_data):
        """Aktualizuje poziom dźwięku na podstawie danych audio"""
        try:
            # Konwertuj dane audio na numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Oblicz RMS (Root Mean Square) jako miarę głośności
            rms = np.sqrt(np.mean(audio_array**2))
            
            # Normalizuj do zakresu 0.0 - 1.0
            # Maksymalna wartość dla 16-bit audio to 32767
            self.audio_level = min(rms / 5000.0, 1.0)  # Dzielimy przez 5000 dla lepszej czułości
            
            # Dodaj do historii (zachowaj tylko ostatnie 50 próbek)
            self.audio_history.append(self.audio_level)
            if len(self.audio_history) > 50:
                self.audio_history.pop(0)
                
        except Exception as e:
            # W przypadku błędu, ustaw poziom na 0
            self.audio_level = 0.0
    
    def animate_wave(self):
        """Animuje falę dźwiękową reagującą na poziom dźwięku"""
        if not self.animation_running or self.canvas is None:
            return
            
        self.canvas.delete("all")
        
        # Parametry fali
        width = 180
        height = 40
        center_y = height // 2
        
        # Użyj poziomu dźwięku do kontroli amplitudy fali
        base_amplitude = 5 + (self.audio_level * 20)  # Amplituda od 5 do 25
        
        # Rysuj główną falę reagującą na dźwięk
        points = []
        for x in range(0, width, 2):
            # Podstawowa fala z animacją
            base_wave = math.sin((x + self.animation_frame * 3) * 0.1)
            
            # Dodaj wpływ poziomu dźwięku
            audio_influence = self.audio_level * math.sin((x + self.animation_frame * 5) * 0.15)
            
            # Kombinuj obie fale
            wave_height = base_amplitude * (base_wave + audio_influence * 0.5)
            y = center_y + wave_height
            points.extend([x, y])
        
        if len(points) >= 4:
            # Kolor zależy od poziomu dźwięku
            intensity = int(255 * (0.3 + self.audio_level * 0.7))
            color = f"#{intensity:02x}0000"  # Od ciemnoczerwonego do jasnoczerwnego
            self.canvas.create_line(points, fill=color, width=2, smooth=True)
        
        # Dodaj dodatkowe fale z historią dźwięku
        if len(self.audio_history) > 10:
            for i in range(min(3, len(self.audio_history) // 10)):
                points2 = []
                history_index = -(i + 1) * 10
                if abs(history_index) <= len(self.audio_history):
                    historical_level = self.audio_history[history_index]
                    amplitude = 3 + (historical_level * 10)
                    
                    for x in range(0, width, 3):
                        wave_height = amplitude * math.sin((x + self.animation_frame * 2 + i * 30) * 0.08)
                        y = center_y + wave_height
                        points2.extend([x, y])
                    
                    if len(points2) >= 4:
                        alpha = 0.7 - (i * 0.2)
                        intensity = int(255 * alpha * (0.3 + historical_level * 0.7))
                        color = f"#{intensity:02x}{int(intensity * 0.3):02x}{int(intensity * 0.3):02x}"
                        self.canvas.create_line(points2, fill=color, width=1, smooth=True)
        
        self.animation_frame += 1
        
        # Zaplanuj następną klatkę animacji
        if self.window:
            self.window.after(30, self.animate_wave)  # Szybsza animacja (30ms)
    
    def hide(self):
        """Ukrywa okienko nagrywania"""
        self.animation_running = False
        if self.window is not None:
            self.window.destroy()
            self.window = None
            self.canvas = None

class VoiceNotes:
    def __init__(self):
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
        
        # Inicjalizacja okienka nagrywania
        self.recording_window = RecordingWindow()
        
        print("✅ OpenAI Whisper API skonfigurowane pomyślnie!")
        
    def start_recording(self):
        """Rozpoczyna nagrywanie dźwięku"""
        if self.is_recording:
            return
            
        self.is_recording = True
        print("\n🎤 NAGRYWANIE ROZPOCZĘTE - mów teraz...")
        print("Naciśnij ponownie Windows+Ctrl aby zatrzymać nagrywanie")
        
        # Pokaż okienko nagrywania
        self.recording_window.show()
        
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording(self):
        """Zatrzymuje nagrywanie dźwięku"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        print("⏹️ NAGRYWANIE ZATRZYMANE - przetwarzanie...")
        
        # Ukryj okienko nagrywania
        self.recording_window.hide()
        
        if self.recording_thread:
            self.recording_thread.join(timeout=2)
    
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
            keyboard.send('ctrl+v')
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
        """Konfiguruje globalny skrót klawiszowy Windows+Ctrl"""
        def on_hotkey():
            self.toggle_recording()
        
        try:
            # Kombinacja Windows + Ctrl
            self.hotkey_listener = pynput_keyboard.GlobalHotKeys({
                '<cmd>+<ctrl>': on_hotkey
            })
            self.hotkey_listener.start()
            print("🔥 Skrót klawiszowy Windows+Ctrl został aktywowany!")
            return True
        except Exception as e:
            print(f"❌ Błąd podczas konfiguracji skrótu klawiszowego: {e}")
            return False
    
    def run(self):
        """Uruchamia aplikację"""
        print("=" * 60)
        print("🎙️  NOTATNIK GŁOSOWY - OpenAI Whisper")
        print("=" * 60)
        print("📋 Instrukcje:")
        print("• Naciśnij Windows+Ctrl aby rozpocząć/zatrzymać nagrywanie")
        print("• Mów wyraźnie po polsku")
        print("• Tekst zostanie wyświetlony w terminalu")
        print("• Jeśli aktywne jest pole tekstowe, tekst zostanie wklejony")
        print("• Naciśnij Ctrl+C aby zakończyć program")
        print("• Używa OpenAI Whisper API dla najlepszej jakości rozpoznawania")
        print("=" * 60)
        
        if not self.setup_hotkey():
            print("❌ Nie udało się skonfigurować skrótu klawiszowego")
            return
        
        try:
            print("✅ Aplikacja działa! Oczekiwanie na skrót klawiszowy...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Zamykanie aplikacji...")
            if self.hotkey_listener:
                self.hotkey_listener.stop()
            if self.is_recording:
                self.stop_recording()
            # Zamknij okienko nagrywania jeśli jest otwarte
            self.recording_window.hide()
            self.audio.terminate()

def main():
    """Funkcja główna"""
    try:
        app = VoiceNotes()
        app.run()
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        input("Naciśnij Enter aby zakończyć...")

if __name__ == "__main__":
    main()