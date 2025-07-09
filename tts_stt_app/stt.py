import os
import whisper # OpenAI Whisper
import json
try:
    from vosk import Model as VoskModel, KaldiRecognizer, SetLogLevel
    VOSK_AVAILABLE = True
    SetLogLevel(-1) # Suppress Vosk log messages by default
except ImportError:
    VOSK_AVAILABLE = False
    print("Vosk library not found. Vosk STT will be unavailable.")

from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .forms import STTForm, STTTextForm # STTTextForm for displaying/downloading text
from .models import db, ConversionLog
from datetime import datetime
import uuid

stt_bp = Blueprint('stt', __name__, url_prefix='/stt')

# --- Whisper Model Configuration ---
WHISPER_MODEL_NAME = "tiny" # Changed from "tiny.en" to "tiny" for multilingual support
# WHISPER_MODEL_NAME = "base" # Alternative: larger but more accurate multilingual model

# Directory where models are stored or will be downloaded.
# This path should be tts_stt_app/models/whisper_models/
MODELS_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models'))
WHISPER_DOWNLOAD_ROOT = os.path.join(MODELS_BASE_DIR, 'whisper_models') # e.g., tts_stt_app/models/whisper_models
if not os.path.exists(WHISPER_DOWNLOAD_ROOT):
    os.makedirs(WHISPER_DOWNLOAD_ROOT)

# Expected path for the .pt model file (e.g., tts_stt_app/models/whisper_models/tiny.pt)
EXPECTED_MODEL_PT_PATH = os.path.join(WHISPER_DOWNLOAD_ROOT, f"{WHISPER_MODEL_NAME}.pt")

whisper_model = None
if WHISPER_MODEL_NAME: # Only load if a model name is configured
    try:
        print(f"Attempting to load Whisper model: {WHISPER_MODEL_NAME}")
        if os.path.exists(EXPECTED_MODEL_PT_PATH):
            print(f"Found pre-downloaded Whisper model at: {EXPECTED_MODEL_PT_PATH}")
            whisper_model = whisper.load_model(EXPECTED_MODEL_PT_PATH)
        else:
            print(f"Whisper model .pt file not found at {EXPECTED_MODEL_PT_PATH}. Attempting to download '{WHISPER_MODEL_NAME}' to {WHISPER_DOWNLOAD_ROOT}...")
            whisper_model = whisper.load_model(WHISPER_MODEL_NAME, download_root=WHISPER_DOWNLOAD_ROOT)
        print(f"Whisper model '{WHISPER_MODEL_NAME}' loaded successfully.")
    except Exception as e:
        print(f"Error loading Whisper model '{WHISPER_MODEL_NAME}': {e}")
        print(f"Please ensure the model '{WHISPER_MODEL_NAME}.pt' is available in '{WHISPER_DOWNLOAD_ROOT}' or that the application has internet access to download it.")
        whisper_model = None # Keep it as None, routes should check this

# --- Vosk Model Configuration & Loading ---
VOSK_MODELS_DIR = os.path.join(MODELS_BASE_DIR, 'vosk_models') # e.g., tts_stt_app/models/vosk_models
if not os.path.exists(VOSK_MODELS_DIR):
    os.makedirs(VOSK_MODELS_DIR)

loaded_vosk_models = {} # Cache for loaded Vosk models: {'en-us': VoskModel_instance}

def get_vosk_model(lang_code="en-us"):
    """Loads a Vosk model for the given language code. Assumes models are in VOSK_MODELS_DIR/model-<lang_code>"""
    if not VOSK_AVAILABLE:
        return None
    if lang_code in loaded_vosk_models:
        return loaded_vosk_models[lang_code]

    # Example model path: VOSK_MODELS_DIR/vosk-model-small-en-us-0.15 or VOSK_MODELS_DIR/en-us
    # The form provides 'en-us'. We need to map this to an actual model directory name.
    # For simplicity, let's assume the directory is named exactly as the lang_code from the form,
    # or a predefined mapping.
    # For now, let's assume the directory is named e.g., 'en-us' inside VOSK_MODELS_DIR
    model_path = os.path.join(VOSK_MODELS_DIR, lang_code) # e.g., tts_stt_app/models/vosk_models/en-us

    if not os.path.exists(model_path):
        print(f"Vosk model for '{lang_code}' not found at {model_path}. Please download and place it there.")
        # Example: Download from https://alphacephei.com/vosk/models and extract to VOSK_MODELS_DIR/en-us
        return None
    try:
        print(f"Loading Vosk model for '{lang_code}' from {model_path}...")
        model = VoskModel(model_path)
        loaded_vosk_models[lang_code] = model
        print(f"Vosk model for '{lang_code}' loaded successfully.")
        return model
    except Exception as e:
        print(f"Error loading Vosk model for '{lang_code}': {e}")
        return None

# Pre-load default Vosk model if VOSK is available (optional, can be loaded on demand)
# if VOSK_AVAILABLE:
#     get_vosk_model("en-us") # Example: pre-load English US model

ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a', 'ogg', 'flac', 'aac'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_user_text_dir(user_id):
    text_dir = os.path.join(os.path.dirname(__file__), 'static', 'text', str(user_id))
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
    return text_dir

# Need pydub for audio conversion for Vosk
from pydub import AudioSegment

def ensure_user_dir(base_folder_name, user_id): # More generic version
    # Path relative to the app's root directory (where app.py is)
    dir_path = os.path.join(current_app.root_path, 'static', base_folder_name, str(user_id))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def transcribe_with_vosk(audio_filepath, lang_code="en-us"):
    vosk_model_instance = get_vosk_model(lang_code)
    if not vosk_model_instance:
        return None, f"Vosk model for '{lang_code}' not available or failed to load."

    converted_wav_path = None # Define outside try block for cleanup
    try:
        # Vosk requires WAV PCM 16-bit mono. Convert using pydub.
        converted_wav_path = audio_filepath + "_vosk_mono.wav"

        sound = AudioSegment.from_file(audio_filepath)
        sound = sound.set_channels(1) # Mono
        sound = sound.set_frame_rate(16000) # 16kHz is common for Vosk models
        sound.export(converted_wav_path, format="wav")

        wf = open(converted_wav_path, "rb")
        # Use the model's sample rate if available, else default (16000)
        sample_rate = sound.frame_rate # Or vosk_model_instance.sample_rate if model object exposes it
        rec = KaldiRecognizer(vosk_model_instance, sample_rate)
        rec.SetWords(True)

        full_transcription_parts = []
        while True:
            data = wf.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result_json = rec.Result()
                result_dict = json.loads(result_json)
                full_transcription_parts.append(result_dict.get('text', ''))

        final_result_json = rec.FinalResult()
        final_result_dict = json.loads(final_result_json)
        full_transcription_parts.append(final_result_dict.get('text', ''))

        wf.close()

        final_text = " ".join(filter(None, full_transcription_parts)).strip()
        # Language is known from lang_code for Vosk.
        return final_text, lang_code

    except Exception as e:
        print(f"Error during Vosk transcription for {audio_filepath} with lang {lang_code}: {e}")
        return None, str(e)
    finally:
        if converted_wav_path and os.path.exists(converted_wav_path):
            os.remove(converted_wav_path) # Clean up temporary converted WAV

@stt_bp.route('/transcribe', methods=['GET', 'POST'])
@login_required
def transcribe():
    form = STTForm()
    text_form = STTTextForm()

    # Dynamically populate Vosk language choices based on found model directories
    if VOSK_AVAILABLE:
        try:
            available_vosk_model_dirs = [d for d in os.listdir(VOSK_MODELS_DIR) if os.path.isdir(os.path.join(VOSK_MODELS_DIR, d))]
            form.vosk_language.choices = [(model_dir, model_dir.replace('-', ' ').replace('_', ' ').title()) for model_dir in available_vosk_model_dirs]
            if not form.vosk_language.choices:
                form.vosk_language.choices = [("", "No Vosk models found in models/vosk_models")]
        except FileNotFoundError:
            form.vosk_language.choices = [("", "Vosk models directory not found")]
            print(f"Vosk models directory not found at {VOSK_MODELS_DIR}")
    else: # Vosk not available
        form.vosk_language.choices = [("", "Vosk not available")]
        # Hide Vosk engine choice if not available? Or let it show and error out.
        # For now, let it show, error handling below will catch it.
        # Or, better: filter engine choices if an engine is unavailable.
        if ('vosk', 'Vosk (Language Specific Models, Faster, Lighter)') in form.stt_engine.choices:
            form.stt_engine.choices = [choice for choice in form.stt_engine.choices if choice[0] != 'vosk']


    if request.method == 'POST' and 'audio_file' in request.files:
        file = request.files['audio_file']
        stt_engine_choice = form.stt_engine.data
        vosk_lang_choice = form.vosk_language.data

        if file.filename == '':
            flash('No selected file.', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            user_temp_uploads_dir = ensure_user_dir('uploads', current_user.id) # Using the generic helper
            temp_audio_path = os.path.join(user_temp_uploads_dir, filename)

            transcribed_text = None
            processed_language = "unknown" # Language used/detected by the engine
            error_message = None

            try:
                file.save(temp_audio_path)

                if stt_engine_choice == 'whisper':
                    if not whisper_model:
                        error_message = "Whisper STT engine is selected, but the model is not available. Please check server logs."
                    else:
                        print(f"Transcribing with Whisper: {temp_audio_path}")
                        transcribe_options = {}
                        result = whisper_model.transcribe(temp_audio_path, **transcribe_options)
                        transcribed_text = result["text"]
                        processed_language = result.get("language", "unknown")

                elif stt_engine_choice == 'vosk':
                    if not VOSK_AVAILABLE:
                        error_message = "Vosk STT engine is selected, but the Vosk library is not installed/available."
                    elif not vosk_lang_choice:
                        error_message = "Vosk STT engine selected, but no Vosk language model was chosen or available."
                    else:
                        print(f"Transcribing with Vosk (lang: {vosk_lang_choice}): {temp_audio_path}")
                        transcribed_text, vosk_error_detail = transcribe_with_vosk(temp_audio_path, vosk_lang_choice)
                        if transcribed_text is None: # Transcription failed
                            error_message = f"Vosk transcription failed: {vosk_error_detail}"
                        else:
                            processed_language = vosk_lang_choice # For Vosk, language is the chosen model
                else:
                    error_message = "Invalid STT engine selected."

                if error_message:
                    flash(error_message, "danger")
                    print(f"STT Error: {error_message}")
                elif transcribed_text is None: # Safeguard if error_message wasn't set but text is None
                    flash("STT process completed but failed to return text.", "danger")
                    print("STT Error: Transcribed text is None without specific error message.")
                else: # Success
                    # Ensure user_text_dir uses the generic ensure_user_dir
                    user_text_output_dir = ensure_user_dir('text', current_user.id)
                    unique_id = uuid.uuid4().hex
                    # Include engine in filename for clarity
                    output_txt_filename = f"stt_{stt_engine_choice}_{processed_language.replace(' ','-')}_{unique_id}.txt"
                    output_txt_filepath = os.path.join(user_text_output_dir, output_txt_filename)

                    with open(output_txt_filepath, 'w', encoding='utf-8') as f:
                        f.write(transcribed_text)

                    new_log = ConversionLog(
                        user_id=current_user.id,
                        type='STT',
                        language=f"{stt_engine_choice}: {processed_language}",
                        output_filename=output_txt_filename
                    )
                    db.session.add(new_log)
                    db.session.commit()

                    flash(f'Audio transcribed successfully with {stt_engine_choice.capitalize()}!', 'success')
                    text_form.transcribed_text.data = transcribed_text

                    return render_template('stt_transcriber.html', form=form, text_form=text_form,
                                           txt_filename=output_txt_filename,
                                           pdf_filename=output_txt_filename.replace('.txt','.pdf'),
                                           result_text_available=True)

            except Exception as e:
                flash(f"An unexpected error occurred during STT processing: {str(e)}", 'danger')
                print(f"STT General Error (post-upload): {e}")
            finally:
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
        else:
            flash(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 'warning')

    return render_template('stt_transcriber.html', form=form, text_form=text_form, txt_filename=None, pdf_filename=None, result_text_available=False)


@stt_bp.route('/download_text/<type>/<filename>')
@login_required
def download_stt_text(type, filename):
    user_text_dir = ensure_user_text_dir(current_user.id) # Path relative to the blueprint file

    actual_filepath = os.path.join(user_text_dir, filename)

    if not os.path.exists(actual_filepath):
         flash("File not found or access denied.", "danger")
         return redirect(url_for('stt.transcribe'))

    if type == "txt":
        return send_from_directory(user_text_dir, filename, as_attachment=True)
    elif type == "pdf":
        # PDF generation will be implemented here using fpdf or reportlab
        # For now, let's provide a placeholder or redirect
        from .utils.pdf_tools import create_pdf_from_text_file # Assuming this function exists

        pdf_filename = filename.replace('.txt', '.pdf')
        pdf_filepath = os.path.join(user_text_dir, pdf_filename)

        try:
            if not create_pdf_from_text_file(actual_filepath, pdf_filepath):
                 flash("Could not generate PDF.", "danger")
                 return redirect(url_for('stt.transcribe'))
            return send_from_directory(user_text_dir, pdf_filename, as_attachment=True)
        except Exception as e:
            flash(f"Error generating PDF: {str(e)}", "danger")
            return redirect(url_for('stt.transcribe'))

    flash("Invalid download type.", "danger")
    return redirect(url_for('stt.transcribe'))


# TODO:
# 1. Create templates/stt_transcriber.html
# 2. Add 'openai-whisper' to requirements.txt
# 3. Update app.py to register stt_bp
# 4. Update dashboard.html link for STT
# 5. Implement microphone recording (JavaScript + new Flask endpoint)
# 6. Implement PDF generation in utils/pdf_tools.py
# 7. Provide instructions for downloading Whisper models for offline use.
#    (The current code tries to download if not found, but for true offline, it must be pre-downloaded)
# 8. Create 'static/uploads/<user_id>' directory (or handle in ensure_user_upload_dir)
#    The 'uploads' dir should be for temporary storage during transcription.
#    The 'static/text/<user_id>' is for the final .txt/.pdf outputs.

# Create a temporary upload folder (not in static if not directly served)
# For now, putting it in static/uploads for simplicity, but could be instance_path based.
# Ensure 'static/uploads' directory exists (app.py already creates static/audio and static/text)
# We'll need a similar check for 'static/uploads' in app.py or here.
# The `user_upload_dir` is created on the fly in the `transcribe` route.
# However, the base 'static/uploads' itself might need to be ensured.
# This is generally handled by .gitignore for user-generated content folders.
# Let's ensure the base `uploads` directory is created in `app.py` for robustness.
