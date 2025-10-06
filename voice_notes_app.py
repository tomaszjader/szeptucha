"""
Główna klasa aplikacji Voice Notes - zrefaktoryzowana wersja
"""
import tkinter as tk
import sys
from typing import Optional

from config import Config
from audio_recorder import AudioRecorder
from recording_window import RecordingWindow
from transcription_service import TranscriptionService
from hotkey_manager import HotkeyManager
from text_processor import TextProcessor


class VoiceNotesApp:
    """Główna klasa aplikacji Voice Notes"""
    
    def __init__(self, root: tk.Tk):
        """
        Inicjalizuje aplikację Voice Notes
        
        Args:
            root: Główne okno Tkinter
        """
        self.root = root
        
        # Waliduj konfigurację
        try:
            Config.validate()
        except ValueError as e:
            print(f"❌ BŁĄD: {e}")
            sys.exit(1)
        
        # Inicjalizuj komponenty
        self._init_components()
        
        print("✅ Aplikacja Voice Notes została zainicjalizowana!")
    
    def _init_components(self):
        """Inicjalizuje wszystkie komponenty aplikacji"""
        # Inicjalizuj okno nagrywania
        self.recording_window = RecordingWindow(self.root)
        
        # Inicjalizuj recorder audio z callback'iem do okna
        self.audio_recorder = AudioRecorder(
            audio_callback=self.recording_window.update_audio_level
        )
        
        # Inicjalizuj serwis transkrypcji
        self.transcription_service = TranscriptionService()
        
        # Inicjalizuj procesor tekstu
        self.text_processor = TextProcessor()
        
        # Inicjalizuj menedżer skrótów klawiszowych
        self.hotkey_manager = HotkeyManager(self.toggle_recording)
        
        # Stan aplikacji
        self.is_recording = False
    
    def start_recording(self) -> bool:
        """
        Rozpoczyna nagrywanie dźwięku
        
        Returns:
            bool: True jeśli nagrywanie zostało rozpoczęte, False w przeciwnym razie
        """
        if self.is_recording:
            print("⚠️ Nagrywanie już trwa!")
            return False
        
        # Rozpocznij nagrywanie
        if self.audio_recorder.start_recording():
            self.is_recording = True
            # Pokaż okno nagrywania
            self.recording_window.show()
            print("Naciśnij ponownie Ctrl+Alt aby zatrzymać nagrywanie")
            return True
        
        return False
    
    def stop_recording(self):
        """Zatrzymuje nagrywanie dźwięku i przetwarza audio"""
        if not self.is_recording:
            print("⚠️ Nagrywanie nie jest aktywne!")
            return
        
        self.is_recording = False
        
        # Zatrzymaj nagrywanie i pobierz plik audio
        audio_file_path = self.audio_recorder.stop_recording()
        
        # Ukryj okno nagrywania
        self.recording_window.hide()
        
        if audio_file_path:
            # Transkrybuj audio
            text = self.transcription_service.transcribe_audio_file(audio_file_path)
            
            # Usuń tymczasowy plik
            self.audio_recorder.cleanup_temp_file(audio_file_path)
            
            if text:
                # Przetwórz rozpoznany tekst
                self.text_processor.process_recognized_text(text)
            else:
                print("❌ Nie udało się rozpoznać tekstu")
        else:
            print("❌ Nie udało się zapisać pliku audio")
    
    def toggle_recording(self):
        """Przełącza stan nagrywania"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def setup_hotkey(self) -> bool:
        """
        Konfiguruje globalny skrót klawiszowy
        
        Returns:
            bool: True jeśli skrót został skonfigurowany, False w przeciwnym razie
        """
        return self.hotkey_manager.setup_hotkey()
    
    def run(self):
        """Uruchamia aplikację"""
        print("=" * 60)
        print("🎙️  NOTATNIK GŁOSOWY - Whisper (API lub lokalnie)")
        print("=" * 60)
        print("📋 Instrukcje:")
        print("• Naciśnij Ctrl+Alt aby rozpocząć/zatrzymać nagrywanie")
        print("• Mów wyraźnie po polsku")
        print("• Tekst zostanie wyświetlony w terminalu")
        print("• Jeśli aktywne jest pole tekstowe, tekst zostanie wklejony")
        print("• Naciśnij Ctrl+C aby zakończyć program")
        print("• Używa OpenAI Whisper API lub lokalnego modelu (automatyczny wybór)")
        print("=" * 60)
        # Informacja o trybie jeśli dostępna
        try:
            mode = getattr(self.transcription_service, 'mode', None)
            if mode:
                print(f"🔧 Wybrany tryb transkrypcji: {mode}")
        except Exception:
            pass
        
        if not self.setup_hotkey():
            print("❌ Nie udało się skonfigurować skrótu klawiszowego")
            return False
        
        # Uruchom pętlę animacji/komend okienka
        self.recording_window.start()
        print("✅ Aplikacja działa! Oczekiwanie na skrót klawiszowy...")
        return True
    
    def shutdown(self):
        """Zamyka aplikację i zwalnia zasoby"""
        print("\n👋 Zamykanie aplikacji...")
        
        # Zatrzymaj nagrywanie jeśli jest aktywne
        if self.is_recording:
            self.stop_recording()
        
        # Zatrzymaj skrót klawiszowy
        if self.hotkey_manager:
            self.hotkey_manager.stop_hotkey()
        
        # Ukryj okno nagrywania
        if self.recording_window:
            self.recording_window.hide()
        
        # Zwolnij zasoby audio
        if hasattr(self.audio_recorder, 'audio'):
            try:
                self.audio_recorder.audio.terminate()
            except Exception:
                pass
    
    def get_status(self) -> dict:
        """
        Zwraca status aplikacji
        
        Returns:
            dict: Słownik ze statusem aplikacji
        """
        return {
            'is_recording': self.is_recording,
            'hotkey_active': self.hotkey_manager.is_active() if self.hotkey_manager else False,
            'window_visible': self.recording_window.visible if self.recording_window else False,
            'api_configured': TranscriptionService.is_api_key_configured()
        }