from app import create_app
from extensions import db
from models import Product

app = create_app()

with app.app_context():
    Product.query.delete()  # حذف محصولات قبلی
    db.session.commit()

    products_data = [
        {'name': 'محصول 1', 'price': 10000, 'image_url': 'sample1.jpg', 'category': 'عمومی', 'stock': 10},
        {'name': 'محصول 2', 'price': 11000, 'image_url': 'sample2.jpg', 'category': 'عمومی', 'stock': 15},
        # ... بقیه محصولات تا 10 عدد یا بیشتر
    ]

    for pdata in products_data:
        product = Product(**pdata)
        db.session.add(product)
    db.session.commit()


