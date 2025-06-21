from extensions import db
from flask_login import UserMixin
from datetime import datetime
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------- User ---------------------- #
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    orders = db.relationship('Order', back_populates='user', lazy='dynamic')
    transactions = db.relationship('Transaction', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# ---------------------- Product ---------------------- #
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(100), nullable=True)

    suppliers = db.relationship('Supplier', back_populates='product', lazy='dynamic')

    @property
    def image_full_url(self):
        return url_for('static', filename=f'images/{self.image_url}') if self.image_url else url_for('static', filename='images/sample1.jpg')


# ---------------------- Order ---------------------- #
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    customer_name = db.Column(db.String(100), nullable=True)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='در انتظار پرداخت')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid = db.Column(db.Boolean, default=False)  # پرداخت شده یا نه
    delivery_status = db.Column(db.String(50), default='در حال پردازش')  # وضعیت ارسال

    user = db.relationship('User', back_populates='orders')
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan', lazy='joined')
    payments = db.relationship('Payment', back_populates='order', cascade='all, delete-orphan', lazy='joined')


# ---------------------- OrderItem ---------------------- #
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')
    order = db.relationship('Order', back_populates='items')


# ---------------------- Supplier ---------------------- #
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    product = db.relationship('Product', back_populates='suppliers')


# ---------------------- Payment ---------------------- #
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(10))

    order = db.relationship('Order', back_populates='payments')


# ---------------------- CartItem (Optional Model) ---------------------- #
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship('Product')


# ---------------------- Transaction ---------------------- #
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    debit = db.Column(db.Float, default=0.0)
    credit = db.Column(db.Float, default=0.0)
    description = db.Column(db.String(255))

    user = db.relationship('User', back_populates='transactions')




    
