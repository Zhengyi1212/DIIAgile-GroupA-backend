from flask import Flask
from app.login import login_bp  
from app.sign_up import signup_bp
from app.profile import profile_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.secret_key = "your_secret_key"  # Needed for sessions
    
    
    # Register blueprints
    app.register_blueprint(login_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(profile_bp)
    
    # Enable CORS for the entire app
    CORS(app)
     
    return app