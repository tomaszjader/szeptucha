# 🎙️ Notatnik Głosowy - OpenAI Whisper

Aplikacja do tworzenia notatek głosowych z globalnym skrótem klawiszowym Windows + Ctrl. Nagrywa dźwięk, konwertuje na tekst używając **OpenAI Whisper API** i automatycznie wkleja w aktywnym polu tekstowym lub wyświetla w terminalu.

## ✨ Funkcjonalności

- 🔥 **Globalny skrót klawiszowy**: Windows + Ctrl
- 🎤 **Nagrywanie dźwięku** z mikrofonu
- 🤖 **OpenAI Whisper API** - najlepsza jakość rozpoznawania mowy
- 🗣️ **Rozpoznawanie mowy** w języku polskim
- 📝 **Automatyczne wklejanie** tekstu w aktywnych polach tekstowych
- 💬 **Wyświetlanie tekstu** w terminalu
- 🔄 **Toggle nagrywania** - ten sam skrót rozpoczyna i zatrzymuje

## 📋 Wymagania

- Windows 10/11
- Python 3.7+
- Mikrofon
- **Klucz API OpenAI** (wymagany!)
- Połączenie internetowe

## 🔑 Konfiguracja OpenAI API

1. **Uzyskaj klucz API**:
   - Przejdź na https://platform.openai.com/api-keys
   - Zaloguj się lub utwórz konto
   - Wygeneruj nowy klucz API

2. **Ustaw zmienną środowiskową**:
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="twój-klucz-api"
   
   # Lub dodaj na stałe w systemie Windows:
   # Ustawienia > System > Informacje > Zaawansowane ustawienia systemu > Zmienne środowiskowe
   ```

## 🚀 Instalacja

1. **Sklonuj lub pobierz pliki**:
   ```bash
   git clone <repository-url>
   cd szeptucha
   ```

2. **Zainstaluj zależności**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Skonfiguruj klucz API OpenAI:**
   
   **Opcja 1: Plik .env (zalecane)**
   - Otwórz plik `.env` w folderze projektu
   - Wklej swój klucz API OpenAI:
   ```
   OPENAI_API_KEY=sk-proj-twój-klucz-api-tutaj
   ```
   
   **Opcja 2: Zmienna środowiskowa**
   ```powershell
   # W PowerShell:
   $env:OPENAI_API_KEY="twój-klucz-api-openai"
   ```

4. **Uzyskaj klucz API OpenAI:**
   - Idź na https://platform.openai.com/api-keys
   - Zaloguj się lub utwórz konto
   - Wygeneruj nowy klucz API
   - Upewnij się, że masz środki na koncie (API jest płatne)

5. **Uruchom aplikację**:
   ```bash
   python voice_notes.py
   ```

## 🎯 Jak używać

1. **Uruchom aplikację** - pojawi się komunikat o gotowości
2. **Naciśnij Windows + Ctrl** aby rozpocząć nagrywanie
3. **Mów wyraźnie** po polsku
4. **Naciśnij ponownie Windows + Ctrl** aby zatrzymać nagrywanie
5. **Tekst zostanie**:
   - Wklejony automatycznie jeśli aktywne jest pole tekstowe
   - Wyświetlony w terminalu w przeciwnym przypadku

## 🔧 Rozwiązywanie problemów

### Błąd instalacji PyAudio
Jeśli wystąpi problem z instalacją PyAudio:
```bash
pip install pipwin
pipwin install pyaudio
```

### Problemy z mikrofonem
- Sprawdź czy mikrofon jest podłączony i działa
- Upewnij się że aplikacja ma dostęp do mikrofonu w ustawieniach Windows

### Problemy ze skrótem klawiszowym
- Uruchom aplikację jako administrator
- Sprawdź czy inny program nie używa tego samego skrótu

### Błędy rozpoznawania mowy
- Sprawdź połączenie internetowe
- Upewnij się że klucz API OpenAI jest poprawny
- Sprawdź czy masz wystarczające środki na koncie OpenAI
- Mów wyraźnie i w odpowiedniej odległości od mikrofonu
- Aplikacja używa OpenAI Whisper API - najlepsze dostępne rozpoznawanie mowy

## 📁 Struktura plików

```
szeptucha/
├── voice_notes.py      # Główny plik aplikacji
├── requirements.txt    # Zależności Python
└── README.md          # Ten plik
```

## 🛠️ Technologie

- **OpenAI Whisper API** - najlepsze rozpoznawanie mowy
- **PyAudio** - nagrywanie dźwięku
- **pynput** - globalne skróty klawiszowe
- **pyperclip** - operacje na schowku
- **pywin32** - integracja z Windows API

## 📝 Licencja

Ten projekt jest dostępny na licencji MIT.

## 🤝 Wsparcie

Jeśli napotkasz problemy lub masz sugestie, utwórz issue w repozytorium.

---
**Uwaga**: Aplikacja wymaga klucza API OpenAI i połączenia internetowego do działania funkcji rozpoznawania mowy. OpenAI Whisper zapewnia znacznie lepszą jakość rozpoznawania niż darmowe alternatywy.