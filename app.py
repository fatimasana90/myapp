import os
from flask import Flask

# ✨ استفاده از اکستنشن‌های جداشده
from extensions import db, login_manager, session, migrate  # ✅ migrate اضافه شد

def create_app():
    app = Flask(__name__)
    basedir = os.path.abspath(os.path.dirname(__file__))

    # تنظیمات اپلیکیشن
    app.config['SECRET_KEY'] = 'mysecret'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

    # تنظیمات سشن
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = os.path.join(basedir, 'flask_session')

    # مقداردهی اولیه اکستنشن‌ها
    db.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    migrate.init_app(app, db)  # ✅ اضافه شد

    login_manager.login_view = 'main.login'

    # جلوگیری از حلقه واردات
    from models import User
    from routes.main_routes import main as main_blueprint

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ثبت بلوپرینت
    app.register_blueprint(main_blueprint)

    return app  # ❌ حذف db.create_all()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)









