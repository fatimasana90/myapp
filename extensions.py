# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
session = Session()
migrate = Migrate() 
