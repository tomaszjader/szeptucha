"""
Moduł do transkrypcji audio z wyborem trybu: OpenAI Whisper API lub lokalny faster-whisper
"""
import os
import tempfile
from typing import Optional
from openai import OpenAI
from config import Config


class TranscriptionService:
    """Klasa odpowiedzialna za transkrypcję audio (API lub lokalnie)"""

    def __init__(self):
        """Inicjalizuje serwis transkrypcji z wyborem trybu"""
        # Waliduj konfigurację
        Config.validate()

        self.mode = None
        self.client = None
        self.local_model = None

        forced_mode = Config.TRANSCRIPTION_MODE

        # Ustal tryb: jeśli 'api' lub 'auto' z kluczem -> API, w przeciwnym razie lokalny
        use_api = (forced_mode == 'api') or (forced_mode == 'auto' and bool(Config.OPENAI_API_KEY))

        if use_api:
            # Inicjalizacja OpenAI klienta
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
            self.mode = 'api'
            print("✅ Tryb transkrypcji: API (OpenAI Whisper)")
        else:
            # Spróbuj zainicjalizować lokalny model faster-whisper
            try:
                from faster_whisper import WhisperModel
                self.local_model = WhisperModel(
                    Config.LOCAL_WHISPER_MODEL,
                    device=Config.LOCAL_DEVICE,
                    compute_type=Config.LOCAL_COMPUTE_TYPE,
                )
                self.mode = 'local'
                print(f"✅ Tryb transkrypcji: lokalny (faster-whisper: {Config.LOCAL_WHISPER_MODEL})")
            except Exception as e:
                # Jeśli wymuszony 'local' — zgłoś błąd; w 'auto' spróbuj fallback do API jeśli jest klucz
                if forced_mode == 'local':
                    raise RuntimeError(
                        f"Błąd inicjalizacji lokalnego modelu Whisper: {e}. Zainstaluj pakiet 'faster-whisper' i upewnij się, że konfiguracja jest poprawna."
                    )
                if Config.OPENAI_API_KEY:
                    self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
                    self.mode = 'api'
                    print("⚠️ Lokalny model niedostępny; używam API (OpenAI Whisper).")
                else:
                    raise RuntimeError(
                        f"Brak lokalnego modelu i klucza API. Zainstaluj 'faster-whisper' lub ustaw OPENAI_API_KEY. Szczegóły: {e}"
                    )
    
    def transcribe_audio_file(self, audio_file_path: str, language: str = "pl") -> Optional[str]:
        """
        Transkrybuje plik audio (API lub lokalny model)

        Args:
            audio_file_path: Ścieżka do pliku audio (WAV zalecany)
            language: Kod języka (domyślnie "pl" dla polskiego)

        Returns:
            Optional[str]: Transkrybowany tekst lub None w przypadku błędu
        """
        if not os.path.exists(audio_file_path):
            print(f"❌ Plik audio nie istnieje: {audio_file_path}")
            return None

        try:
            if self.mode == 'api':
                print("🔄 Przetwarzanie audio przez OpenAI Whisper (API)...")
                with open(audio_file_path, 'rb') as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language,
                    )
                text = transcript.text.strip()
            else:
                print("🔄 Przetwarzanie audio lokalnie (faster-whisper)...")
                segments, _info = self.local_model.transcribe(
                    audio_file_path,
                    language=language,
                )
                text = " ".join(seg.text for seg in segments).strip()

            if text:
                return text
            else:
                print("❌ Nie rozpoznano żadnego tekstu")
                return None

        except Exception as e:
            print(f"❌ Błąd transkrypcji: {e}")
            return None
    
    def transcribe_audio_data(self, audio_data: bytes, language: str = "pl") -> Optional[str]:
        """
        Transkrybuje surowe dane audio (WAV) — API lub lokalnie.

        Args:
            audio_data: Surowe dane audio w formacie WAV
            language: Kod języka (domyślnie "pl" dla polskiego)

        Returns:
            Optional[str]: Transkrybowany tekst lub None w przypadku błędu
        """
        try:
            if self.mode == 'api':
                print("🔄 Przetwarzanie audio przez OpenAI Whisper (API)...")
                from io import BytesIO
                audio_buffer = BytesIO(audio_data)
                audio_buffer.name = "audio.wav"  # OpenAI wymaga nazwy pliku
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer,
                    language=language,
                )
                text = transcript.text.strip()
            else:
                print("🔄 Przetwarzanie audio lokalnie (faster-whisper)...")
                # Zapisz dane do tymczasowego pliku WAV i przetwórz lokalnie
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                try:
                    segments, _info = self.local_model.transcribe(tmp_path, language=language)
                    text = " ".join(seg.text for seg in segments).strip()
                finally:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

            if text:
                return text
            else:
                print("❌ Nie rozpoznano żadnego tekstu")
                return None

        except Exception as e:
            print(f"❌ Błąd transkrypcji: {e}")
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