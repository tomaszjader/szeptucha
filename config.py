"""
Konfiguracja aplikacji Voice Notes
"""
import os
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych z pliku .env
load_dotenv()

class Config:
    """Klasa konfiguracji aplikacji"""
    
    # OpenAI API
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Konfiguracja audio
    AUDIO_CHUNK = 1024
    AUDIO_FORMAT = 'paInt16'  # pyaudio.paInt16
    AUDIO_CHANNELS = 1
    AUDIO_RATE = 44100
    
    # Konfiguracja okna nagrywania
    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 120
    AUDIO_HISTORY_SIZE = 50
    
    # Konfiguracja skrótów klawiszowych
    HOTKEY_COMBINATION = '<ctrl>+<alt>'
    HOTKEY_DEBOUNCE_TIME = 0.7  # sekundy
    
    # Konfiguracja wizualizacji
    ANIMATION_SPEED = 0.1
    WAVE_COLORS = ['#00ff88', '#00cc66', '#009944', '#006622']
    
    @classmethod
    def validate(cls):
        """Waliduje konfigurację"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("Nie znaleziono klucza API OpenAI! Ustaw zmienną środowiskową OPENAI_API_KEY lub dodaj plik .env")
        return True