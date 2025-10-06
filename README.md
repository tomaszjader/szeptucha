# Voice Notes - Notatnik Głosowy

**[🇵🇱 Polski](README.md) | [🇺🇸 English](README.en.md)**

Aplikacja do nagrywania głosu i automatycznej transkrypcji za pomocą OpenAI Whisper API lub lokalnego modelu faster-whisper (automatyczny wybór).

## 🚀 Nowe funkcje w wersji 2.0

- **Zrefaktoryzowana architektura** - kod podzielony na logiczne moduły
- **Lepsza organizacja kodu** - każdy komponent w osobnym pliku
- **Łatwiejsze utrzymanie** - czytelna struktura i separacja odpowiedzialności
- **Rozszerzalność** - łatwe dodawanie nowych funkcji

## 📁 Struktura projektu

```
szeptucha/
├── main.py                    # Główny plik uruchamiający aplikację
├── voice_notes_app.py         # Główna klasa aplikacji
├── config.py                  # Konfiguracja aplikacji
├── audio_recorder.py          # Moduł nagrywania audio
├── recording_window.py        # Interfejs okna nagrywania
├── transcription_service.py   # Integracja z OpenAI Whisper API i lokalnym faster-whisper
├── hotkey_manager.py          # Zarządzanie skrótami klawiszowymi
├── text_processor.py          # Przetwarzanie i wklejanie tekstu
├── voice_notes_original.py    # Oryginalna wersja (backup)
├── requirements.txt           # Zależności Python
├── .env                       # Zmienne środowiskowe (utwórz ręcznie)
└── README.md                  # Ten plik
```

## 🛠️ Instalacja

1. **Sklonuj repozytorium lub pobierz pliki**

2. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Konfiguracja trybu transkrypcji:**

   Domyślnie aplikacja działa w trybie `auto` — jeśli wykryje `OPENAI_API_KEY`, użyje API OpenAI; w przeciwnym razie uruchomi lokalny model.

   Utwórz plik `.env` w katalogu głównym (opcjonalnie):
   ```
   # Klucz API (opcjonalny w trybie auto lub local)
   OPENAI_API_KEY=twój_klucz_api_tutaj

   # Wymuszony tryb: auto | api | local
   TRANSCRIPTION_MODE=auto

   # Ustawienia lokalnego modelu (dla trybu local/auto)
   LOCAL_WHISPER_MODEL=base  # np. tiny, base, small, medium, large-v2
   LOCAL_DEVICE=cpu          # cpu lub cuda
   LOCAL_COMPUTE_TYPE=int8   # np. int8, float32
   ```

## 🎯 Użytkowanie

### Uruchomienie aplikacji

```bash
python main.py
```

### Podstawowe funkcje

- **Ctrl+Alt** - rozpocznij/zatrzymaj nagrywanie
- Mów wyraźnie po polsku
- Tekst zostanie automatycznie wklejony do aktywnego pola tekstowego
- Jeśli nie ma aktywnego pola, tekst zostanie wyświetlony w terminalu

## 🏗️ Architektura

### Moduły aplikacji

1. **`config.py`** - Centralna konfiguracja aplikacji
2. **`audio_recorder.py`** - Obsługa nagrywania dźwięku
3. **`recording_window.py`** - Wizualne okno z animacją podczas nagrywania
4. **`transcription_service.py`** - Integracja z OpenAI Whisper API
5. **`hotkey_manager.py`** - Globalne skróty klawiszowe
6. **`text_processor.py`** - Wykrywanie pól tekstowych i wklejanie
7. **`voice_notes_app.py`** - Główna logika aplikacji
8. **`main.py`** - Punkt wejścia aplikacji

### Zalety nowej architektury

- **Separacja odpowiedzialności** - każdy moduł ma jasno określoną rolę
- **Łatwość testowania** - komponenty można testować niezależnie
- **Możliwość rozszerzania** - łatwe dodawanie nowych funkcji
- **Czytelność kodu** - mniejsze, bardziej zrozumiałe pliki
- **Ponowne wykorzystanie** - moduły można używać w innych projektach

## 🔧 Konfiguracja

Wszystkie ustawienia znajdują się w pliku `config.py`:

- Parametry audio (częstotliwość, kanały, itp.)
- Ustawienia okna nagrywania
- Konfiguracja skrótów klawiszowych
- Kolory i animacje

## 🚨 Wymagania systemowe

- **Python 3.7+**
- **Windows** (ze względu na biblioteki win32)
- **Mikrofon** do nagrywania
- W trybie lokalnym wymagany jest pakiet `faster-whisper` (dodany do `requirements.txt`). Dla lepszej wydajności na GPU konieczna jest konfiguracja środowiska CUDA.
- W trybie API wymagany jest **klucz API OpenAI** z dostępem do Whisper

## 📝 Zmiany w wersji 2.0

### Refaktoryzacja

- Podzielono monolityczny plik na 8 modułów
- Wprowadzono centralną konfigurację
- Poprawiono obsługę błędów
- Dodano dokumentację kodu

### Nowe funkcje

- Lepsze wykrywanie pól tekstowych
- Ulepszona wizualizacja nagrywania
- Bardziej niezawodne skróty klawiszowe
- Lepsze zarządzanie zasobami

## 🐛 Rozwiązywanie problemów

### Błędy instalacji

Jeśli masz problemy z instalacją `pyaudio`:
```bash
pip install pipwin
pipwin install pyaudio
```

### Problemy z kluczem API

Upewnij się, że:
- Klucz API jest poprawny
- Masz dostęp do Whisper API
- Plik `.env` jest w głównym katalogu

### Problemy ze skrótami klawiszowymi

- Uruchom jako administrator jeśli to konieczne
- Sprawdź czy inne aplikacje nie używają tego samego skrótu

## 📄 Licencja

Ten projekt jest dostępny na licencji MIT.

## 🤝 Wkład w projekt

Zachęcamy do zgłaszania błędów i propozycji ulepszeń!

---

**Wersja 2.0** - Zrefaktoryzowana architektura dla lepszej organizacji kodu