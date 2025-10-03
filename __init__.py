"""
Voice Notes - Aplikacja do nagrywania i transkrypcji głosu
"""

__version__ = "2.0.0"
__author__ = "Voice Notes Team"
__description__ = "Aplikacja do nagrywania głosu i transkrypcji za pomocą OpenAI Whisper"

from .voice_notes_app import VoiceNotesApp
from .config import Config

__all__ = ['VoiceNotesApp', 'Config']