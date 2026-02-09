import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from config import config
from models import db, User
from utils.logging_config import setup_logging

# Create Flask app
def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # CORS - restricted to specific origins
    CORS(app, origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE'])

    # CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["100 per hour", "20 per minute"],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    )

    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Setup logging
    setup_logging(app)

    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMP_FOLDER'], exist_ok=True)
    os.makedirs('templates/auth', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp)

    # Exempt API routes from CSRF (use token-based auth instead)
    csrf.exempt(api_bp)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html',
                             message='Page not found',
                             code=404), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html',
                             message='Access forbidden',
                             code=403), 403

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f'Server error: {str(e)}', exc_info=True)
        return render_template('error.html',
                             message='Internal server error',
                             code=500), 500

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('error.html',
                             message='File too large',
                             code=413), 413

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template('error.html',
                             message='Rate limit exceeded. Please try again later.',
                             code=429), 429

    # Create database tables
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
