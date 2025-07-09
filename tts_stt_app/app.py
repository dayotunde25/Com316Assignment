import os
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap5 # For WTForms Bootstrap styling

from .models import db, User, init_db as init_database
from .auth import auth_bp
from .tts import tts_bp
from .stt import stt_bp

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key_here_change_me') # IMPORTANT: Change this in production!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Ensure database directory exists
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # Ensure static/audio and static/text directories exist
    static_audio_dir = os.path.join(os.path.dirname(__file__), 'static', 'audio')
    if not os.path.exists(static_audio_dir):
        os.makedirs(static_audio_dir)
    static_text_dir = os.path.join(os.path.dirname(__file__), 'static', 'text')
    if not os.path.exists(static_text_dir):
        os.makedirs(static_text_dir)
    static_uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads') # For temporary STT uploads
    if not os.path.exists(static_uploads_dir):
        os.makedirs(static_uploads_dir)


    # Initialize extensions
    Bootstrap5(app) # For Bootstrap styling of WTForms
    CSRFProtect(app)
    init_database(app) # Initialize database using the function from models.py

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Where to redirect if @login_required
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tts_bp)
    app.register_blueprint(stt_bp)

    # Basic routes
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    @login_required # Ensure only logged-in users can access
    def dashboard():
        user_logs = ConversionLog.query.filter_by(user_id=current_user.id).order_by(ConversionLog.timestamp.desc()).all()
        return render_template('dashboard.html', logs=user_logs)

    @app.route('/delete_log/<int:log_id>', methods=['POST'])
    @login_required
    def delete_log(log_id):
        log_entry = ConversionLog.query.get_or_404(log_id)

        if log_entry.user_id != current_user.id:
            flash("You do not have permission to delete this log.", "danger")
            return redirect(url_for('dashboard'))

        try:
            file_to_delete_path = None
            if log_entry.type == 'TTS':
                # Construct path relative to the 'static' folder for os.path.join
                # app.static_folder is the absolute path to the static directory
                # We need to construct path from where app.py is (tts_stt_app)
                # static_dir = os.path.join(os.path.dirname(__file__), 'static')
                # file_to_delete_path = os.path.join(static_dir, 'audio', str(current_user.id), log_entry.output_filename)

                # Simpler using current_app.root_path which is tts_stt_app directory
                file_to_delete_path = os.path.join(current_app.root_path, 'static', 'audio', str(current_user.id), log_entry.output_filename)
            elif log_entry.type == 'STT':
                file_to_delete_path = os.path.join(current_app.root_path, 'static', 'text', str(current_user.id), log_entry.output_filename)
                # Also delete associated PDF if it exists
                pdf_filename = log_entry.output_filename.replace('.txt', '.pdf')
                pdf_to_delete_path = os.path.join(current_app.root_path, 'static', 'text', str(current_user.id), pdf_filename)
                if os.path.exists(pdf_to_delete_path):
                    os.remove(pdf_to_delete_path)


            if file_to_delete_path and os.path.exists(file_to_delete_path):
                os.remove(file_to_delete_path)
                flash(f"File {log_entry.output_filename} deleted.", "info")
            elif file_to_delete_path:
                flash(f"File {log_entry.output_filename} not found, but log entry will be deleted.", "warning")

            db.session.delete(log_entry)
            db.session.commit()
            flash("Log entry deleted successfully.", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting log or file: {str(e)}", "danger")
            print(f"Error during deletion: {e}")

        return redirect(url_for('dashboard'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
