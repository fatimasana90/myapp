from flask import session

def add_product_to_cart(product):
    cart = session.get('cart', {})

    product_id = str(product.id)
    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {
            'name': product.name,
            'price': product.price,
            'quantity': 1,
            'image_url': product.image_url
        }

    session['cart'] = cart
    session.modified = True  # 🔥 این خط حتماً اضافه شود
