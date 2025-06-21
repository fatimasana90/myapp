from app import app, db
from models import User, Payment
from datetime import datetime
from werkzeug.security import generate_password_hash

with app.app_context():
    # حذف اطلاعات قبلی
    Payment.query.delete()
    User.query.delete()
    db.session.commit()

    # ساخت جداول (در صورت نبود)
    db.create_all()

    # 👤 ایجاد کاربر تستی با رمز عبور هش‌شده
    hashed_password = generate_password_hash("test123", method='sha256')
    user = User(
        username='ali',
        email='ali@example.com',
        password=hashed_password  # باید مطمئن باشی فیلد password توی مدل User هست
    )
    db.session.add(user)
    db.session.commit()

    # 💸 پرداخت‌های تستی
    payments = [
        Payment(user_id=user.id, amount=200000, type='debit', date=datetime(2024, 1, 1)),
        Payment(user_id=user.id, amount=150000, type='credit', date=datetime(2024, 1, 3)),
        Payment(user_id=user.id, amount=50000, type='debit', date=datetime(2024, 1, 5)),
    ]
    db.session.add_all(payments)
    db.session.commit()

    print("✅ دیتابیس و کاربر تستی با پرداخت‌ها ساخته شد.")




