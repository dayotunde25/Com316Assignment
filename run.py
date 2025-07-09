from tts_stt_app.app import create_app
from tts_stt_app.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # This will create tables based on models.py if they don't exist
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts
