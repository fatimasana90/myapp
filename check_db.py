from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

try:
    with app.app_context():
        db.create_all()
    print("✅ دیتابیس بدون خطا ساخته شد.")
except Exception as e:
    print(f"❌ خطا در ساخت دیتابیس: {e}")
