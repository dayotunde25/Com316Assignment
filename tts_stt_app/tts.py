import os
import pyttsx3
from flask import Blueprint, render_template, request, send_from_directory, flash, redirect, url_for
from flask_login import login_required, current_user
from .forms import TTSForm
from .models import db, ConversionLog
from datetime import datetime
import uuid # For generating unique filenames
from pydub import AudioSegment

tts_bp = Blueprint('tts', __name__, url_prefix='/tts')

# Ensure user-specific audio directory exists function
def ensure_user_audio_dir(user_id):
    audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio', str(user_id))
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    return audio_dir

@tts_bp.route('/convert', methods=['GET', 'POST'])
@login_required
def convert():
    form = TTSForm()
    output_filename = None
    output_filepath_relative = None

    if form.validate_on_submit():
        text_to_convert = form.text.data
        language = form.language.data # This will be used more with eSpeak/Festival

        try:
            # --- TTS Engine Selection ---
            # Prioritize eSpeak for broader language support, fallback to pyttsx3 if eSpeak fails or for specific cases.
            # For this implementation, we'll primarily use eSpeak if available.

            user_audio_dir = ensure_user_audio_dir(current_user.id)
            unique_id = uuid.uuid4().hex
            temp_wav_filename = f"tts_output_{unique_id}.wav" # eSpeak outputs WAV
            temp_wav_filepath = os.path.join(user_audio_dir, temp_wav_filename)
            output_mp3_filename = f"tts_output_{unique_id}.mp3"
            output_mp3_filepath = os.path.join(user_audio_dir, output_mp3_filename)

            espeak_success = False
            tts_engine_choice = form.tts_engine.data
            # festival_voice_choice = form.festival_voice.data # If Festival voice selection is added

            wav_generated_by_engine = False

            if tts_engine_choice == 'espeak':
                try:
                    import subprocess
                    try: # Check if espeak is available
                        subprocess.run(['espeak', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        flash("eSpeak engine selected, but eSpeak not found or not working. Try another engine or install eSpeak.", "warning")
                        raise NotImplementedError("eSpeak not available")

                    espeak_lang_option = language
                    command = ['espeak', '-v', espeak_lang_option, '-w', temp_wav_filepath, text_to_convert]
                    subprocess.run(command, check=True, capture_output=True, text=True)
                    wav_generated_by_engine = True
                    print(f"eSpeak generated WAV: {temp_wav_filepath}")
                except (NotImplementedError, subprocess.CalledProcessError, FileNotFoundError) as e_espeak:
                    flash(f"eSpeak processing failed: {e_espeak}. Try another engine.", "danger")
                    print(f"eSpeak processing error: {e_espeak}")

            elif tts_engine_choice == 'festival':
                try:
                    import subprocess
                    # Check if text2wave (Festival utility) is available
                    try:
                        subprocess.run(['text2wave', '-h'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # Simple check
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        flash("Festival engine selected, but 'text2wave' (Festival utility) not found. Try another engine or install Festival.", "warning")
                        raise NotImplementedError("Festival (text2wave) not available")

                    # Festival language/voice selection is complex.
                    # Default is often English. Specific voices are loaded via Scheme commands or options.
                    # For simplicity, we'll rely on default voice or user having configured Festival.
                    # A more advanced setup would allow specifying a voice from Festival's installed voices.
                    # E.g. (voice_kal_diphone), (voice_cmu_us_slt_arctic_hts)
                    # We can try to pass a language if text2wave supports a simple lang flag,
                    # but often it's about loading the correct voice within festival itself.
                    # For now, no explicit language/voice switching for festival via command line here.
                    # It will use its default voice.

                    # Using text2wave: text2wave [options] textfile -o output.wav
                    # We need to pass text via stdin or a temporary file. Stdin is cleaner.
                    process = subprocess.run(
                        ['text2wave', '-o', temp_wav_filepath],
                        input=text_to_convert,
                        text=True,
                        check=True,
                        capture_output=True
                    )
                    wav_generated_by_engine = True
                    print(f"Festival generated WAV: {temp_wav_filepath}")
                except (NotImplementedError, subprocess.CalledProcessError, FileNotFoundError) as e_festival:
                    flash(f"Festival processing failed: {e_festival}. Try another engine.", "danger")
                    print(f"Festival processing error: {e_festival}")

            elif tts_engine_choice == 'pyttsx3':
                try:
                    engine = pyttsx3.init()
                    voices = engine.getProperty('voices')
                    selected_voice = None
                    for voice in voices:
                        if language in voice.languages or language == voice.id.split('_')[-1]:
                            selected_voice = voice.id
                            break
                    if selected_voice: engine.setProperty('voice', selected_voice)
                    else: print(f"pyttsx3: No specific voice for '{language}', using default.")

                    engine.save_to_file(text_to_convert, temp_wav_filepath)
                    engine.runAndWait()
                    wav_generated_by_engine = True
                    print(f"pyttsx3 generated WAV: {temp_wav_filepath}")
                except Exception as e_pyttsx3:
                    flash(f"pyttsx3 processing failed: {str(e_pyttsx3)}. Try another engine.", 'danger')
                    print(f"pyttsx3 Error: {e_pyttsx3}")

            else:
                flash("Invalid TTS engine selected.", "danger")


            # If WAV generation was successful by any engine
            if wav_generated_by_engine and os.path.exists(temp_wav_filepath):
                try:
                    audio = AudioSegment.from_wav(temp_wav_filepath)
                    audio.export(output_mp3_filepath, format="mp3")
                    os.remove(temp_wav_filepath)
                    output_filename = output_mp3_filename
                    output_filepath_relative = os.path.join('audio', str(current_user.id), output_filename)
                    flash('Text converted to MP3 successfully!', 'success')
                except Exception as e_conv:
                    flash(f"Error converting WAV to MP3: {str(e_conv)}. Serving WAV instead (if available).", 'warning')
                    print(f"MP3 Conversion Error: {e_conv}")
                    # Fallback to WAV if MP3 conversion fails but WAV exists
                    if os.path.exists(temp_wav_filepath): # Should not happen if successfully removed
                        output_filename = temp_wav_filename
                        output_filepath_relative = os.path.join('audio', str(current_user.id), output_filename)
                    else: # This case means WAV was made, MP3 failed, and WAV somehow vanished. Unlikely.
                         flash("Critical error in audio file handling after conversion attempt.", "danger")
                         return render_template('tts_player.html', form=form, audio_file_url=None, filename=None)
            else:
                flash("TTS WAV file generation failed.", "danger")
                return render_template('tts_player.html', form=form, audio_file_url=None, filename=None)

            # Save to database
            # Include the engine in the log. The 'language' field might need context if it's engine-specific.
            # For now, 'language' stores the user's selection from the dropdown.
            # We could enhance 'language' to be like 'tts_engine:language_code' if needed for clarity.
            # Or add a new 'engine_details' field to ConversionLog model.
            # For now, let's try to fit it into 'language' or assume 'input_text' can give context.
            # Let's modify the log to be clearer: language = f"{tts_engine_choice}:{language}"
            new_log = ConversionLog(
                user_id=current_user.id,
                type='TTS',
                language=f"{tts_engine_choice}:{language}", # Store engine and language
                input_text=text_to_convert,
                output_filename=output_filename # Store relative path from static/
            )
            db.session.add(new_log)
            db.session.commit()

            flash('Text converted to speech successfully!', 'success')
            # Pass the relative path for use in url_for('static', ...)
            return render_template('tts_player.html', form=form, audio_file_url=url_for('static', filename=output_filepath_relative), filename=output_filename)

        except Exception as e:
            flash(f"Error during TTS conversion: {str(e)}", 'danger')
            print(f"TTS Error: {e}") # For debugging

    return render_template('tts_player.html', form=form, audio_file_url=None, filename=None)


@tts_bp.route('/download/<filename>')
@login_required
def download_tts_audio(filename):
    user_audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio', str(current_user.id))
    # Security check: ensure the file belongs to the user's directory (basic check)
    if not os.path.exists(os.path.join(user_audio_dir, filename)):
         flash("File not found or access denied.", "danger")
         return redirect(url_for('tts.convert'))
    return send_from_directory(user_audio_dir, filename, as_attachment=True)

# Need a template for TTS interaction and player
# templates/tts_player.html
# This will be created in the next step.

# Need to update app.py to register this blueprint
# And requirements.txt for pyttsx3, pydub
# And install ffmpeg for pydub MP3 export. Instructions for this will be in README.md.
