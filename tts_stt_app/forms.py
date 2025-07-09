from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import User

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TTSForm(FlaskForm):
    text = TextAreaField('Text to Convert', validators=[DataRequired(), Length(min=1, max=5000)])
    language = SelectField('Language', choices=[
        ('en', 'English'), ('fr', 'French'), ('es', 'Spanish'),
        ('ar', 'Arabic'), ('yo', 'Yoruba'), ('ha', 'Hausa'), ('ig', 'Igbo')
        # Add more languages as supported by chosen engine
    ], validators=[DataRequired()])
    tts_engine = SelectField('TTS Engine', choices=[
        ('espeak', 'eSpeak (Broad language support, robotic)'),
        ('festival', 'Festival (Potentially more natural, setup intensive)'),
        ('pyttsx3', 'pyttsx3 (System voices, quality varies)')
    ], default='espeak', validators=[DataRequired()])
    # Festival voice selection could be added if needed, similar to Vosk language
    # festival_voice = SelectField('Festival Voice', choices=[('kal_diphone', 'English (Kal Diphone - Default)'), ...], validators=[])
    submit = SubmitField('Convert to Speech')

class STTForm(FlaskForm):
    # Field for file upload (handled separately in template/JS for now)
    # language = SelectField('Language (leave blank to auto-detect for Whisper)', choices=[
    #     ('', 'Auto-Detect (Whisper)'), ('en', 'English'), ('fr', 'French'), ('es', 'Spanish'),
    #     ('ar', 'Arabic'), ('yo', 'Yoruba'), ('ha', 'Hausa'), ('ig', 'Igbo')
    #     # Add more languages as supported
    # ]) # Optional: if explicit language choice is desired over auto-detect
    stt_engine = SelectField('Transcription Engine', choices=[
        ('whisper', 'Whisper (Multilingual, Slower, Higher Accuracy)'),
        ('vosk', 'Vosk (Language Specific Models, Faster, Lighter)')
    ], default='whisper', validators=[DataRequired()])
    vosk_language = SelectField('Vosk Language Model', choices=[
        ('en-us', 'English (US)'),
        # Add paths to other Vosk models here, e.g. ('fr-fr', 'French')
        # These choices should map to available Vosk model directories/names.
        # This field will be shown/hidden by JS based on stt_engine selection.
    ], validators=[]) # Optional validator if Vosk is selected
    submit_upload = SubmitField('Transcribe Uploaded File')
    submit_record = SubmitField('Transcribe Recording') # This might be triggered by JS

class STTTextForm(FlaskForm):
    transcribed_text = TextAreaField('Transcribed Text', validators=[DataRequired()])
    download_txt = SubmitField('Download .txt')
    download_pdf = SubmitField('Download .pdf')
