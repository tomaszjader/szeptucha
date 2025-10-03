"""
Moduł do nagrywania dźwięku
"""
import pyaudio
import threading
import wave
import tempfile
import os
from typing import Callable, Optional, List
from config import Config


class AudioRecorder:
    """Klasa odpowiedzialna za nagrywanie dźwięku"""
    
    def __init__(self, audio_callback: Optional[Callable[[bytes], None]] = None):
        """
        Inicjalizuje recorder audio
        
        Args:
            audio_callback: Funkcja wywoływana z danymi audio podczas nagrywania
        """
        self.audio = pyaudio.PyAudio()
        self.audio_callback = audio_callback
        
        # Konfiguracja audio z config
        self.chunk = Config.AUDIO_CHUNK
        self.format = getattr(pyaudio, Config.AUDIO_FORMAT)
        self.channels = Config.AUDIO_CHANNELS
        self.rate = Config.AUDIO_RATE
        
        # Stan nagrywania
        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.frames: List[bytes] = []
        self._stream: Optional[pyaudio.Stream] = None
    
    def start_recording(self) -> bool:
        """
        Rozpoczyna nagrywanie dźwięku
        
        Returns:
            bool: True jeśli nagrywanie zostało rozpoczęte, False w przeciwnym razie
        """
        if self.is_recording:
            print("⚠️ Nagrywanie już trwa!")
            return False
            
        # Upewnij się, że poprzedni wątek nagrywania został zakończony
        if self.recording_thread and self.recording_thread.is_alive():
            print("⚠️ Czekam na zakończenie poprzedniego nagrywania...")
            self.recording_thread.join(timeout=3)
            
        self.is_recording = True
        self.frames = []  # Wyczyść poprzednie dane audio
        print("\n🎤 NAGRYWANIE ROZPOCZĘTE - mów teraz...")
        
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
        
        return True
    
    def stop_recording(self) -> Optional[str]:
        """
        Zatrzymuje nagrywanie dźwięku i zwraca ścieżkę do pliku audio
        
        Returns:
            Optional[str]: Ścieżka do tymczasowego pliku WAV lub None w przypadku błędu
        """
        if not self.is_recording:
            print("⚠️ Nagrywanie nie jest aktywne!")
            return None
            
        self.is_recording = False
        print("⏹️ NAGRYWANIE ZATRZYMANE - przetwarzanie...")
        
        # Poczekaj na zakończenie wątku nagrywania
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=5)
            
        # Wyczyść referencję do wątku
        self.recording_thread = None
        
        # Zapisz audio do pliku
        return self._save_audio_to_file()
    
    def _record_audio(self):
        """Nagrywa dźwięk w osobnym wątku"""
        try:
            # Rozpocznij nagrywanie
            self._stream = self.audio.open(
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
                try:
                    data = self._stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # Przekaż dane audio do callback'a jeśli jest ustawiony
                    if self.audio_callback:
                        self.audio_callback(data)
                        
                except Exception as e:
                    print(f"⚠️ Błąd podczas odczytu audio: {e}")
                    break
            
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None
            
        except Exception as e:
            print(f"❌ Błąd podczas nagrywania: {e}")
            self.is_recording = False
    
    def _save_audio_to_file(self) -> Optional[str]:
        """
        Zapisuje nagrane audio do tymczasowego pliku WAV
        
        Returns:
            Optional[str]: Ścieżka do pliku lub None w przypadku błędu
        """
        if not self.frames:
            print("❌ Brak danych audio do zapisania")
            return None
            
        try:
            # Utwórz tymczasowy plik WAV
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_file.close()
            
            # Zapisz audio do pliku WAV
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.frames))
            
            return temp_file.name
            
        except Exception as e:
            print(f"❌ Błąd podczas zapisywania audio: {e}")
            return None
    
    def cleanup_temp_file(self, file_path: str):
        """
        Usuwa tymczasowy plik audio
        
        Args:
            file_path: Ścieżka do pliku do usunięcia
        """
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"⚠️ Nie udało się usunąć tymczasowego pliku: {e}")
    
    def __del__(self):
        """Destruktor - zwalnia zasoby audio"""
        try:
            if self._stream:
                self._stream.stop_stream()
                self._stream.close()
            self.audio.terminate()
        except Exception:
            pass