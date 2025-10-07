# Voice Notes - Voice Recorder

**[🇵🇱 Polski](README.md) | [🇺🇸 English](README.en.md)**

An application for voice recording and automatic transcription using OpenAI Whisper API or a local faster-whisper model (automatic selection).

## 🚀 New features in version 2.0

- **Refactored architecture** - code divided into logical modules
- **Better code organization** - each component in a separate file
- **Easier maintenance** - clear structure and separation of responsibilities
- **Extensibility** - easy addition of new features

## 📁 Project structure

```
szeptucha/
├── main.py                    # Main application launcher file
├── voice_notes_app.py         # Main application class
├── config.py                  # Application configuration
├── audio_recorder.py          # Audio recording module
├── recording_window.py        # Recording window interface
├── transcription_service.py   # OpenAI Whisper API and local faster-whisper integration
├── hotkey_manager.py          # Keyboard shortcuts management
├── text_processor.py          # Text processing and pasting
├── voice_notes_original.py    # Original version (backup)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create manually)
└── README.md                  # This file
```

## 🛠️ Installation

1. **Clone the repository or download files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Transcription mode configuration:**

   By default, the app runs in `auto` mode — if `OPENAI_API_KEY` is detected, it will use the OpenAI API; otherwise, it will run a local model.

   Create a `.env` file in the root directory (optional):
   ```
   # API key (optional in auto or local mode)
   OPENAI_API_KEY=your_api_key_here

   # Forced mode: auto | api | local
   TRANSCRIPTION_MODE=auto

   # Local model settings (for local/auto)
   LOCAL_WHISPER_MODEL=base  # e.g., tiny, base, small, medium, large-v2
   LOCAL_DEVICE=cpu          # cpu or cuda
   LOCAL_COMPUTE_TYPE=int8   # e.g., int8, float32
   ```

## 🎯 Usage

### Running the application

```bash
python main.py
```

### Basic functions

- **Ctrl+Alt** - start/stop recording
- Speak clearly in Polish
- Text will be automatically pasted into the active text field
- If there's no active field, text will be displayed in the terminal

## 🏗️ Architecture

### Application modules

1. **`config.py`** - Central application configuration
2. **`audio_recorder.py`** - Audio recording handling
3. **`recording_window.py`** - Visual window with animation during recording
4. **`transcription_service.py`** - OpenAI Whisper API integration
5. **`hotkey_manager.py`** - Global keyboard shortcuts
6. **`text_processor.py`** - Text field detection and pasting
7. **`voice_notes_app.py`** - Main application logic
8. **`main.py`** - Application entry point

### Advantages of the new architecture

- **Separation of concerns** - each module has a clearly defined role
- **Easy testing** - components can be tested independently
- **Extensibility** - easy addition of new features
- **Code readability** - smaller, more understandable files
- **Reusability** - modules can be used in other projects

## 🔧 Configuration

All settings are located in the `config.py` file:

- Audio parameters (frequency, channels, etc.)
- Recording window settings
- Keyboard shortcuts configuration
- Colors and animations

## 🚨 System requirements

- **Python 3.7+**
- **Windows** (due to win32 libraries)
- **Microphone** for recording
- For local mode, the `faster-whisper` package is required (added to `requirements.txt`). For better GPU performance, a proper CUDA environment is needed.
- For API mode, an **OpenAI API key** with Whisper access is required

## 📝 Changes in version 2.0

### Refactoring

- Split monolithic file into 8 modules
- Introduced central configuration
- Improved error handling
- Added code documentation

### New features

- Better text field detection
- Improved recording visualization
- More reliable keyboard shortcuts
- Better resource management

## 🐛 Troubleshooting

### Installation errors

If you have problems installing `pyaudio`:
```bash
pip install pipwin
pipwin install pyaudio
```

#### Permission/install issues on Windows

- If installing `faster-whisper` throws “Could not install packages due to an OSError” or mentions `pyav.exe.deleteme`, try:
  - `python -m pip install --user --no-warn-script-location --no-cache-dir "faster-whisper>=0.10.0"`
  - Run PowerShell as Administrator.
  - Ensure you use `python -m pip` instead of `pip`.
- Quick local model check:
  - `python -c "from faster_whisper import WhisperModel; print('OK')"`

### API key issues

Make sure that:
- API key is correct
- You have access to Whisper API
- `.env` file is in the root directory

### Keyboard shortcut issues

- Run as administrator if necessary
- Check if other applications aren't using the same shortcut

## 📄 License

This project is available under the MIT license.

## 🤝 Contributing

We encourage reporting bugs and suggesting improvements!

---

**Version 2.0** - Refactored architecture for better code organization