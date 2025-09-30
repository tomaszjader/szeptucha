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

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

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
        
        print("✅ OpenAI Whisper API skonfigurowane pomyślnie!")
        
    def start_recording(self):
        """Rozpoczyna nagrywanie dźwięku"""
        if self.is_recording:
            return
            
        self.is_recording = True
        print("\n🎤 NAGRYWANIE ROZPOCZĘTE - mów teraz...")
        print("Naciśnij ponownie Windows+Ctrl aby zatrzymać nagrywanie")
        
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording(self):
        """Zatrzymuje nagrywanie dźwięku"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        print("⏹️ NAGRYWANIE ZATRZYMANE - przetwarzanie...")
        
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