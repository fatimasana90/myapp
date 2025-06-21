# بالای فایل main/routes.py یا main.py

def apply_product_filters(query, form):
    if form.name.data:
        query = query.filter(Product.name.ilike(f"%{form.name.data}%"))
    if form.category.data:
        query = query.filter(Product.category.ilike(f"%{form.category.data}%"))
    if form.min_price.data is not None:
        query = query.filter(Product.price >= form.min_price.data)
    if form.max_price.data is not None:
        query = query.filter(Product.price <= form.max_price.data)

    sort = form.sort_by.data or 'newest'
    if sort == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort == 'stock':
        query = query.order_by(Product.stock.desc())
    else:
        query = query.order_by(Product.id.desc())

    return query
