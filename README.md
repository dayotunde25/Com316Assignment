# Offline Text-to-Speech (TTS) and Speech-to-Text (STT) Web Application

## 🎯 Objective

This web application provides offline Text-to-Speech (TTS) and Speech-to-Text (STT) conversion capabilities. Authenticated users can convert text into speech, transcribe audio files or microphone input into text, manage their conversion history, and download results, all without relying on internet-based APIs.

## 🧩 Functional Requirements Implemented

*   **User Authentication:** Secure registration, login, and logout. Passwords hashed with `bcrypt`. Session-based authentication via Flask-Login.
*   **Text-to-Speech (TTS):**
    *   Users can input text and select an output language and TTS engine.
    *   Supported engines: eSpeak (multilingual), Festival (multilingual, setup-dependent), pyttsx3 (system voices).
    *   Listen in-browser and download output as `.mp3`.
*   **Speech-to-Text (STT):**
    *   Users can upload audio files (`.mp3`, `.wav`, etc.) or record from microphone (basic implementation).
    *   Select STT engine: Whisper (multilingual, accurate) or Vosk (faster, language-specific models).
    *   View transcribed text and download as `.txt` or `.pdf`.
*   **Multilingual Support:**
    *   TTS: Via eSpeak, Festival, and system-dependent pyttsx3 voices.
    *   STT: Whisper (`tiny` model for broad language auto-detection), Vosk (requires specific language model download).
*   **User Dashboard:** Displays user-specific conversion history with options to play/view, download, and delete logs and associated files.

## ⚙️ Technical Specifications

*   **Backend:** Flask (Python)
    *   RESTful principles for some actions.
    *   Authentication: Flask-Login, bcrypt.
    *   Database: SQLite.
    *   CSRF Protection: Flask-WTF.
*   **Frontend:** HTML5, Bootstrap 5 (served locally), Jinja2 templating, JavaScript for dynamic interactions.
*   **File Conversion & Processing:**
    *   TTS: `espeak` (subprocess), `festival` (subprocess, via `text2wave`), `pyttsx3`.
    *   STT: `openai-whisper`, `vosk`.
    *   Audio Manipulation: `pydub` (requires `ffmpeg`).
    *   PDF Generation: `fpdf2`.

## 📂 Folder Structure

```
tts_stt_app/
├── app.py              # Main Flask application setup, routes for dashboard, delete
├── auth.py             # Authentication blueprint, routes (login, register, logout)
├── tts.py              # TTS blueprint and logic
├── stt.py              # STT blueprint and logic
├── models.py           # SQLAlchemy models (User, ConversionLog)
├── forms.py            # Flask-WTF forms
├── utils/
│   ├── audio_tools.py  # (Currently minimal, pydub used directly)
│   └── pdf_tools.py    # PDF generation utility
├── static/
│   ├── audio/<user_id>/ # Stores TTS audio outputs
│   ├── text/<user_id>/  # Stores STT text/pdf outputs
│   ├── uploads/<user_id>/# Temporary storage for STT uploads
│   ├── css/style.css   # Custom CSS
│   ├── js/             # Custom JS (e.g., for microphone, UI interactions)
│   └── vendor/         # Local vendor libraries (e.g., Bootstrap)
├── templates/          # HTML templates (Jinja2)
│   ├── base.html, index.html, login.html, register.html, dashboard.html,
│   └── tts_player.html, stt_transcriber.html
├── database/
│   └── app.db          # SQLite database file (created on first run)
├── models/             # Root directory for storing downloaded ML models
│   ├── whisper_models/ # For Whisper models (e.g., tiny.pt)
│   └── vosk_models/    # For Vosk language models (e.g., en-us/)
├── fonts/              # For custom fonts like DejaVuSansCondensed.ttf (for PDF unicode)
└── requirements.txt    # Python dependencies
run.py                  # Script to run the Flask development server
```

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   `pip` for installing Python packages
*   `ffmpeg` (system-wide installation)
*   `espeak` or `espeak-ng` (system-wide installation for TTS)
*   `festival` and `text2wave` utility (system-wide installation for TTS, optional)

### Installation & Setup

1.  **Clone the repository (if applicable) or download the files.**
    ```bash
    # git clone <repository_url>
    # cd tts_stt_app_directory
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install System Dependencies for Offline Capabilities:**

    This application is designed to work offline. To achieve this, you need to pre-download/install necessary speech models and engines.

    *   **FFmpeg (for audio conversion):**
        `ffmpeg` is required by `pydub` for audio processing.
        *   Linux: `sudo apt update && sudo apt install ffmpeg`
        *   macOS: `brew install ffmpeg`
        *   Windows: Download binaries from [ffmpeg.org](https://ffmpeg.org/download.html) and add to your system's PATH.

    *   **Speech-to-Text (STT) Models:**
        *   **Whisper Models:**
            The application uses OpenAI's Whisper. By default, it's configured for the `"tiny"` multilingual model.
            *   **Automatic Download (if online during first run):** The app will attempt to download `tiny.pt` to `tts_stt_app/models/whisper_models/`.
            *   **Manual Offline Download:**
                1.  Download `tiny.pt` (or other models like `base.pt`) from links on the [OpenAI Whisper GitHub](https://github.com/openai/whisper#available-models-and-languages).
                2.  Create directory: `tts_stt_app/models/whisper_models/`
                3.  Place the downloaded `.pt` file (e.g., `tiny.pt`) into this directory.

        *   **Vosk Models:**
            Vosk uses language-specific models.
            1.  **Model Download:** Get models from [Vosk Model Page](https://alphacephei.com/vosk/models). E.g., for US English, download `vosk-model-small-en-us-0.15.zip`.
            2.  **Installation:**
                *   Create directory: `tts_stt_app/models/vosk_models/`
                *   Extract the downloaded model. It creates a folder like `vosk-model-small-en-us-0.15`.
                *   **Rename this folder to the language code** you'll use in the app (e.g., rename to `en-us`).
                *   Place this renamed folder (e.g., `en-us`) inside `tts_stt_app/models/vosk_models/`.
                    Final path example: `tts_stt_app/models/vosk_models/en-us/...model_files...`
                *   The app populates the "Vosk Language Model" dropdown based on subdirectory names found in `tts_stt_app/models/vosk_models/`.

    *   **Text-to-Speech (TTS) Engines:**
        *   **eSpeak NG:**
            *   Linux: `sudo apt update && sudo apt install espeak-ng`
            *   macOS: `brew install espeak` (or `espeak-ng` if available)
            *   Windows: Download from [eSpeak NG GitHub Releases](https://github.com/espeak-ng/espeak-ng/releases). Add to PATH.
            *   Ensure `espeak-ng-data` is installed for language support.

        *   **Festival (Optional):**
            *   Linux: `sudo apt update && sudo apt install festival festvox-kallpc16k` (for a common English voice). Other voices/languages (e.g., Spanish, French) require different `festvox-*` packages.
            *   macOS/Windows: Installation is more complex.
            *   The app uses `text2wave` utility, which must be in PATH. Festival uses its default voice unless system-wide configurations specify others for different languages.

        *   **pyttsx3 (Fallback):**
            Relies on OS-level TTS engines (SAPI5 on Windows, NSSpeechSynthesizer on macOS, etc.). No extra install beyond `pip install pyttsx3`, but voice quality/language support varies by OS.

    *   **Fonts for PDF (Recommended for Unicode):**
        For best character support in generated PDFs:
        1.  Download `DejaVuSansCondensed.ttf` (e.g., from [DejaVu Fonts](https://dejavu-fonts.github.io/)).
        2.  Create directory: `tts_stt_app/fonts/`.
        3.  Place `DejaVuSansCondensed.ttf` into `tts_stt_app/fonts/`.
        The app attempts to use this font; if not found, it falls back to standard PDF fonts with limited Unicode. The `pdf_tools.py` file has logic to try and load `DejaVuSansCondensed.ttf` assuming it's discoverable by FPDF (e.g. in the `FPDF_FONTPATH` or a system font directory). For bundling, placing it in `tts_stt_app/fonts/` is good practice, and `pdf_tools.py` could be updated to explicitly try loading from `../fonts/DejaVuSansCondensed.ttf` relative to its own location.

5.  **Run the application (for development):**
    ```bash
    python run.py
    ```
    This script runs the Flask development server with `debug=True`. **Do not use the development server in a production environment.**
    The application will be accessible at `http://127.0.0.1:5001` (or `http://localhost:5001`). The first run will create the SQLite database file `tts_stt_app/database/app.db`.

### 💨 Basic Usage

1.  **Register** a new user account.
2.  **Login** with your credentials.
3.  From the **Dashboard**:
    *   Navigate to **Text-to-Speech (TTS)**:
        *   Enter text, select language, choose a TTS engine (eSpeak, Festival, pyttsx3).
        *   Click "Convert to Speech".
        *   Listen to the audio output or download it as an MP3.
    *   Navigate to **Speech-to-Text (STT)**:
        *   Choose an STT engine (Whisper or Vosk).
        *   If Vosk, select a downloaded language model.
        *   Upload an audio file.
        *   Click "Transcribe Uploaded File".
        *   View the transcribed text and download as `.txt` or `.pdf`.
        *   (Microphone recording is a basic placeholder and needs further development for full functionality).
4.  **Conversion History** on the Dashboard lists all your past TTS/STT operations with options to Play/View, Download, or Delete entries and associated files.

## 🔐 Security Notes
*   Uses `bcrypt` for password hashing.
*   CSRF protection is enabled for forms submitted via POST.
*   User-specific data is segregated in separate directories where applicable.
*   **IMPORTANT**: Ensure `app.config['SECRET_KEY']` in `tts_stt_app/app.py` is changed to a strong, unique secret key for any production or shared deployment. The default key is for development only.
*   The application runs with `debug=True` when using `run.py`. This is **not suitable for production**. Use a production-ready WSGI server (like Gunicorn or Waitress) for deployment.

## 🛠️ Further Enhancements (Future Scope from Original Plan)
*   Full microphone recording and processing for STT (currently placeholder UI).
*   Admin panel for user management or global file cleanup.
*   Per-user settings (default languages, voices).
*   Offline language translation capabilities.
*   Advanced voice controls (pitch, speed) for TTS engines that support these options via command line.
*   Dark mode toggle for the UI.
*   Desktop packaging (e.g., via Electron or Tauri).

## 📄 License
This project is unlicensed and free to use. (Or specify a license if you have one).
```
