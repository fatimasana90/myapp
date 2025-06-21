from utils.cart import add_product_to_cart
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort, current_app
from flask import send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
import logging

from forms import LoginForm, RegisterForm, AddProductForm, ProductSearchForm
from models import db, User, Product, Order, OrderItem, Payment
from utils.filters import apply_product_filters

main = Blueprint('main', __name__)

# === Utility functions ===
def add_product_to_cart(product):
    cart = session.get('cart', {})
    str_id = str(product.id)
    if str_id in cart:
        cart[str_id]['quantity'] += 1
    else:
        cart[str_id] = {
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': 1
        }
    session['cart'] = cart
    session.modified = True

# ---------------------- Home ---------------------- #
@main.route('/')
def home():
    try:
        show_all = request.args.get('show_all', 'false').lower() == 'true'

        if show_all:
            products_query = Product.query.all()
        else:
            products_query = Product.query.limit(4).all()

        total_count = Product.query.count()

        if not products_query:
            # محصولات پیش‌فرض
            default_products = [
                {'id': 1001, 'name': 'نبات فله', 'price': 10000, 'image_url': url_for('static', filename='images/novelty_item1.jpg'), 'category': 'غذایی', 'stock': 50},
                {'id': 1002, 'name': 'نبات کاوردار', 'price': 12000, 'image_url': url_for('static', filename='images/novelty_item2.jpg'), 'category': 'غذایی', 'stock': 30},
                {'id': 1003, 'name': 'تک نفره', 'price': 12000, 'image_url': url_for('static', filename='images/novelty_item2.jpg'), 'category': 'غذایی', 'stock': 30},
                {'id': 1004, 'name': 'لبی قلیان', 'price': 12000, 'image_url': url_for('static', filename='images/novelty_item2.jpg'), 'category': 'غذایی', 'stock': 30},
            ]
            return render_template('index.html', products=default_products, total_count=len(default_products), show_all=show_all)

        products = [{
            'id': p.id,
            'name': p.name,
            'price': p.price,
            'image_url': p.image_url or url_for('static', filename='images/sample1.jpg'),
            'category': p.category,
            'stock': p.stock
        } for p in products_query]

        return render_template('index.html', products=products, total_count=total_count, show_all=show_all)

    except Exception as e:
        logging.exception("خطا در دریافت داده‌ها")
        flash(f"خطا در دریافت داده‌ها: {str(e)}")
        # نمایش پیش‌فرض در صورت خطا
        fallback_products = [
            {'id': 1001, 'name': 'نبات فله', 'price': 10000, 'image_url': url_for('static', filename='images/novelty_item1.jpg'), 'category': 'غذایی', 'stock': 50},
            {'id': 1002, 'name': 'نبات کاوردار', 'price': 12000, 'image_url': url_for('static', filename='images/novelty_item2.jpg'), 'category': 'غذایی', 'stock': 30},
        ]
        return render_template('index.html', products=fallback_products, total_count=len(fallback_products), show_all=False)




# ---------------------- Auth ---------------------- #
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('ایمیل قبلاً ثبت شده است.', 'warning')
            return redirect(url_for('main.register'))
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('ثبت‌نام با موفقیت انجام شد.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    next_page = request.args.get('next')
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('ورود موفقیت‌آمیز بود.', 'success')
            return redirect(next_page or url_for('main.home'))
        flash('ایمیل یا رمز عبور اشتباه است.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('با موفقیت خارج شدید.', 'info')
    return redirect(url_for('main.home'))

# ---------------------- Products ---------------------- #
@main.route('/products')
def products():
    form = ProductSearchForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = 6

    query = Product.query

    # اعمال فیلترها
    if form.name.data:
        query = query.filter(Product.name.ilike(f"%{form.name.data}%"))

    if form.category.data:
        query = query.filter(Product.category.ilike(f"%{form.category.data}%"))

    if form.min_price.data is not None:
        query = query.filter(Product.price >= form.min_price.data)

    if form.max_price.data is not None:
        query = query.filter(Product.price <= form.max_price.data)

    # مرتب‌سازی
    if form.sort_by.data == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif form.sort_by.data == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif form.sort_by.data == 'stock':
        query = query.order_by(Product.stock.desc())
    else:  # 'newest' یا پیش‌فرض
        query = query.order_by(Product.id.desc())

    try:
        pagination = query.paginate(page=page, per_page=per_page)
        return render_template('products.html', products=pagination.items, form=form, pagination=pagination)
    except Exception as e:
        logging.exception("خطا در دریافت محصولات")
        flash(f"خطا در دریافت محصولات: {str(e)}", 'danger')
        return render_template('products.html', products=[], form=form)

# مسیر AJAX فقط محتوای محصولات برمی‌گردونه
@main.route('/products/ajax')
def products_ajax():
    form = ProductSearchForm(request.args)
    query = Product.query

    if form.name.data:
        query = query.filter(Product.name.ilike(f"%{form.name.data}%"))
    if form.category.data:
        query = query.filter(Product.category.ilike(f"%{form.category.data}%"))
    if form.min_price.data:
        query = query.filter(Product.price >= form.min_price.data)
    if form.max_price.data:
        query = query.filter(Product.price <= form.max_price.data)

    sort = form.sort_by.data
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'stock':
        query = query.order_by(Product.stock.desc())
    else:
        query = query.order_by(Product.id.desc())

    products = query.all()
    return render_template('partials/_product_list.html', products=products)

@main.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    form = AddProductForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data:
            file = form.image.data
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']:
                filename = secure_filename(file.filename)
                unique_name = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
                file.save(filepath)
                image_url = unique_name
        product = Product(
            name=form.name.data,
            stock=form.stock.data,
            price=form.price.data,
            category=form.category.data,
            image_url=image_url
        )
        db.session.add(product)
        db.session.commit()
        flash('محصول با موفقیت اضافه شد.', 'success')
        return redirect(url_for('main.products'))
    return render_template('add_product.html', form=form)

@main.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    previous_url = request.referrer or url_for('main.products')

    return render_template('product_detail.html', product=product, previous_url=previous_url)


# ---------------------- Cart ---------------------- #
@main.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)


@main.route('/add_to_cart/<int:product_id>', methods=['POST'])  # باید POST باشه!
def add_to_cart(product_id):
    try:
        product = Product.query.get_or_404(product_id)

        cart = session.get('cart', {})
        product_id_str = str(product.id)

        if product_id_str in cart:
            cart[product_id_str]['quantity'] += 1
        else:
            cart[product_id_str] = {
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': 1
            }

        session['cart'] = cart
        flash('✅ محصول به سبد اضافه شد.', 'success')
    except Exception as e:
        logging.exception("❌ خطا در افزودن به سبد خرید")
        flash(f'خطا در افزودن به سبد خرید: {str(e)}', 'danger')

    return redirect(request.referrer or url_for('main.home'))


@main.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    flash('سبد خرید پاک شد.')
    return redirect(url_for('main.cart'))

@main.route('/account')
@login_required
def account():
    transactions = current_user.transactions
    records = []
    balance = 0
    for tx in transactions:
        balance += tx.credit - tx.debit
        records.append({
            'date': tx.date.strftime('%Y-%m-%d'),
            'debit': tx.debit if tx.debit > 0 else None,
            'credit': tx.credit if tx.credit > 0 else None,
            'balance': balance
        })
    return render_template('account.html', records=records)

@main.route('/favorites')
@login_required
def favorites():
    return render_template('favorites.html')


@main.route('/api/cart', methods=['POST'])
@login_required
def api_add_to_cart():
    try:
        data = request.get_json()

        if not data or 'id' not in data:
            return jsonify({'message': 'شناسه محصول ارسال نشده است.'}), 400

        product_id = int(data['id'])
        print("🟡 Product ID received from frontend:", product_id)

        product = Product.query.get(product_id)
        if not product:
            return jsonify({'message': 'محصول پیدا نشد.'}), 404

        add_product_to_cart(product)

        return jsonify({'message': f'✅ {product.name} به سبد خرید اضافه شد.'}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.exception("❌ API خطا در افزودن به سبد خرید")
        return jsonify({
            'message': '❌ خطا در افزودن به سبد خرید',
            'error': str(e)
        }), 500

# ---------------------- order ---------------------- #

@main.route('/order_history')
@login_required
def order_history():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('order_history.html', orders=user_orders)

@main.route('/pending_orders')
@login_required
def pending_orders():
    orders = Order.query.filter_by(user_id=current_user.id, status='pending').all()
    return render_template('pending_orders.html', orders=orders)

@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('سبد خرید شما خالی است.', 'warning')
        return redirect(url_for('main.cart'))

    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        email = request.form.get('email', '').strip()

        errors = []
        if not name:
            errors.append('لطفا نام کامل را وارد کنید.')
        if not address:
            errors.append('لطفا آدرس را وارد کنید.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            # فرم را دوباره با مقادیر ارسال شده رندر کن تا کاربر داده‌ها را از دست ندهد
            return render_template('checkout.html', cart=cart, total=total_price, form_data={'name': name, 'address': address, 'email': email})

        new_order = Order(
            user_id=current_user.id,
            customer_name=name,
            total_price=total_price,
            status='در انتظار پرداخت',
            # اگر فیلد آدرس و ایمیل در مدل دارید، اینجا اضافه کنید
            # address=address,
            # email=email
        )
        db.session.add(new_order)
        db.session.commit()

        for item in cart.values():
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )
            db.session.add(order_item)
        db.session.commit()

        session.pop('cart', None)
        flash('سفارش شما ثبت شد.', 'success')
        return redirect(url_for('main.payment_page', order_id=new_order.id))

    # GET request: نمایش فرم سفارش
    return render_template('checkout.html', cart=cart, total=total_price, form_data={})



@main.route('/payment/<int:order_id>', methods=['GET', 'POST'])
@login_required
def payment_page(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        order.paid = True
        order.status = 'پرداخت شده'
        db.session.commit()
        flash('پرداخت با موفقیت انجام شد.', 'success')
        return redirect(url_for('main.receipt', order_id=order.id))

    return render_template('payment.html', order=order)

@main.route('/receipt/<int:order_id>')
@login_required
def receipt(order_id):
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        abort(403)

    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template('receipt.html', order=order, items=order_items)

@main.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    # امنیت: فقط کاربر خودش بتونه سفارش خودشو ببینه
    if order.user_id != current_user.id:
        abort(403)

    return render_template('order_detail.html', order=order)


@main.route('/thank-you')
@login_required
def thank_you():
    return render_template('thank_you.html')

# ---------------------- admin ---------------------- #

@main.route('/admin')
def admin_dashboard():
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_price)).scalar() or 0
    total_users = User.query.count()
    total_products = Product.query.count()
    return render_template('admin/dashboard.html',
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           total_users=total_users,
                           total_products=total_products)


@main.route('/admin/products')
def admin_products():
    # لیست محصولات
    return render_template('admin/products.html', products=Product.query.all())

@main.route('/admin/orders')
def admin_orders():
    # لیست سفارش‌ها
    return render_template('admin/orders.html', orders=Order.query.all())

@main.route('/admin/order/<int:order_id>', methods=['GET', 'POST'])
def view_invoice(order_id):
    order = Order.query.get_or_404(order_id)
    if request.method == 'POST':
        new_status = request.form.get('status')
        order.status = new_status
        db.session.commit()
        flash('وضعیت سفارش با موفقیت به‌روزرسانی شد.', 'success')
        return redirect(url_for('view_invoice', order_id=order.id))
    return render_template('admin/order_detail.html', order=order)


@main.route('/admin/reports', methods=['GET', 'POST'])
def reports():
    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        orders = Order.query.filter(Order.created_at.between(start_date, end_date)).all()
        return render_template('admin/reports.html', orders=orders)
    return render_template('admin/reports.html', orders=None)


# ---------------------- load ---------------------- #
@main.route('/load_more')
def load_more():
    try:
        offset = int(request.args.get('offset', 0))
        limit = 4
        products = Product.query.order_by(Product.id.desc()).offset(offset).limit(limit).all()

        if not products and offset == 0:
            # حالت تست: اگر دیتابیس خالی بود، چند محصول فرضی برگردون
            products = [
                {
                    'id': 9991,
                    'name': 'محصول تست ۱',
                    'price': 10000,
                    'image_url': url_for('static', filename='images/sample1.jpg'),
                    'category': 'آزمایشی',
                    'stock': 10
                },
                {
                    'id': 9992,
                    'name': 'محصول تست ۲',
                    'price': 20000,
                    'image_url': url_for('static', filename='images/sample1.jpg'),
                    'category': 'آزمایشی',
                    'stock': 20
                },
            ]
            return jsonify({'success': True, 'products': products})

        product_data = [
            {
                'id': p.id,
                'name': p.name,
                'price': p.price,
                'image_url': url_for('static', filename=f'images/{p.image_url}') if p.image_url else url_for('static', filename='images/sample1.jpg'),
                'category': p.category,
                'stock': p.stock
            } for p in products
        ]
        return jsonify({'success': True, 'products': product_data})
    except Exception as e:
        logging.exception("خطا در بارگذاری بیشتر محصولات")
        return jsonify({'success': False, 'message': f'خطا در بارگذاری محصولات: {str(e)}'}), 500

# ---------------------- mobile/routes.py ---------------------- #


@main.route('/mobile')
def mobile_home():
    categories = [
        {"id": 1, "name": "خوراکی", "icon": "🍞"},
        {"id": 2, "name": "شوینده", "icon": "🧴"},
        {"id": 3, "name": "پلاستیکی", "icon": "🍽️"},
        {"id": 4, "name": "نوشیدنی", "icon": "🧃"},
        {"id": 5, "name": "دستمال", "icon": "🧻"},
    ]

    products = [
        {"id": 101, "name": "روغن مایع 1.8L", "price": 98000, "category_id": 1, "image": "https://via.placeholder.com/400x180"},
        {"id": 102, "name": "مایع ظرفشویی", "price": 46000, "category_id": 2, "image": "https://via.placeholder.com/400x180"},
        {"id": 103, "name": "لیوان یک‌بار مصرف", "price": 32000, "category_id": 3, "image": "https://via.placeholder.com/400x180"},
    ]

    return render_template('mobile_home.html', categories=categories, products=products)

@main.route('/mobile/cart')
def mobile_cart():
    return render_template('mobile_cart.html')

@main.route('/mobile/checkout')
def mobile_checkout():
    return render_template('mobile_checkout.html')

@main.route('/mobile/profile')
def mobile_profile():
    return render_template('mobile_profile.html')

@main.route('/mobile/product/<int:product_id>')
def mobile_product_detail(product_id):
    products = [
        {"id": 1, "name": "برنج طارم", "price": 650000, "image": "/static/images/rice.jpg", "description": "برنج ایرانی با کیفیت بالا", "category": "خوراکی"},
        {"id": 2, "name": "مایع ظرفشویی", "price": 95000, "image": "/static/images/liquid.jpg", "description": "مایع ظرفشویی ۴ لیتری مناسب رستوران", "category": "شوینده"},
    ]
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return "محصول یافت نشد", 404
    return render_template('mobile_product_detail.html', product=product)



@main.route('/manifest_mobile.json')
def manifest():
    return send_from_directory('static', 'manifest_mobile.json')


