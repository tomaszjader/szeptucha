# Voice Notes - Notatnik Głosowy

**[🇵🇱 Polski](README.md) | [🇺🇸 English](README.en.md)**

Aplikacja do nagrywania głosu i automatycznej transkrypcji za pomocą OpenAI Whisper API.

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
├── transcription_service.py   # Integracja z OpenAI Whisper
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

3. **Skonfiguruj klucz API OpenAI:**
   
   Utwórz plik `.env` w katalogu głównym:
   ```
   OPENAI_API_KEY=twój_klucz_api_tutaj
   ```
   
   Lub ustaw zmienną środowiskową:
   ```bash
   set OPENAI_API_KEY=twój_klucz_api_tutaj
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
- **Klucz API OpenAI** z dostępem do Whisper

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