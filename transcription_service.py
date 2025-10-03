"""
Moduł do transkrypcji audio za pomocą OpenAI Whisper
"""
import os
from typing import Optional
from openai import OpenAI
from config import Config


class TranscriptionService:
    """Klasa odpowiedzialna za transkrypcję audio za pomocą OpenAI Whisper"""
    
    def __init__(self):
        """Inicjalizuje serwis transkrypcji"""
        # Waliduj konfigurację
        Config.validate()
        
        # Inicjalizacja OpenAI klienta
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        print("✅ OpenAI Whisper API skonfigurowane pomyślnie!")
    
    def transcribe_audio_file(self, audio_file_path: str, language: str = "pl") -> Optional[str]:
        """
        Transkrybuje plik audio za pomocą OpenAI Whisper
        
        Args:
            audio_file_path: Ścieżka do pliku audio
            language: Kod języka (domyślnie "pl" dla polskiego)
            
        Returns:
            Optional[str]: Transkrybowany tekst lub None w przypadku błędu
        """
        if not os.path.exists(audio_file_path):
            print(f"❌ Plik audio nie istnieje: {audio_file_path}")
            return None
            
        try:
            print("🔄 Przetwarzanie audio przez OpenAI Whisper...")
            
            with open(audio_file_path, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            text = transcript.text.strip()
            
            if text:
                print(f"\n📝 ROZPOZNANY TEKST:")
                print(f"'{text}'")
                print("-" * 50)
                return text
            else:
                print("❌ Nie rozpoznano żadnego tekstu")
                return None
                
        except Exception as e:
            print(f"❌ Błąd OpenAI API: {e}")
            return None
    
    def transcribe_audio_data(self, audio_data: bytes, language: str = "pl") -> Optional[str]:
        """
        Transkrybuje surowe dane audio za pomocą OpenAI Whisper
        
        Args:
            audio_data: Surowe dane audio w formacie WAV
            language: Kod języka (domyślnie "pl" dla polskiego)
            
        Returns:
            Optional[str]: Transkrybowany tekst lub None w przypadku błędu
        """
        try:
            print("🔄 Przetwarzanie audio przez OpenAI Whisper...")
            
            # Utwórz obiekt podobny do pliku z danych audio
            from io import BytesIO
            audio_buffer = BytesIO(audio_data)
            audio_buffer.name = "audio.wav"  # OpenAI wymaga nazwy pliku
            
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_buffer,
                language=language
            )
            
            text = transcript.text.strip()
            
            if text:
                print(f"\n📝 ROZPOZNANY TEKST:")
                print(f"'{text}'")
                print("-" * 50)
                return text
            else:
                print("❌ Nie rozpoznano żadnego tekstu")
                return None
                
        except Exception as e:
            print(f"❌ Błąd OpenAI API: {e}")
            return None
    
    @staticmethod
    def is_api_key_configured() -> bool:
        """
        Sprawdza czy klucz API OpenAI jest skonfigurowany
        
        Returns:
            bool: True jeśli klucz jest skonfigurowany, False w przeciwnym razie
        """
        try:
            Config.validate()
            return True
        except ValueError:
            return False
    
    @staticmethod
    def get_supported_languages():
        """
        Zwraca listę obsługiwanych języków
        
        Returns:
            dict: Słownik z kodami języków i ich nazwami
        """
        return {
            "pl": "Polski",
            "en": "English",
            "de": "Deutsch",
            "fr": "Français",
            "es": "Español",
            "it": "Italiano",
            "pt": "Português",
            "ru": "Русский",
            "ja": "日本語",
            "ko": "한국어",
            "zh": "中文"
        }