from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
