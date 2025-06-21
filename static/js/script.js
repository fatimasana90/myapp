window.addEventListener("DOMContentLoaded", () => {
  // 🔹 بوت‌استرپ اسلایدر
  const carouselElement = document.querySelector('#carouselExampleIndicators');
  if (carouselElement && typeof bootstrap !== "undefined") {
    new bootstrap.Carousel(carouselElement, {
      interval: 30000,
      ride: 'carousel'
    });
  }

  // 🔹 عناصر منوی کناری
  const menuToggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  let overlay = document.getElementById('overlay');

  // 🔹 اگر overlay وجود نداشت، بساز
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'overlay';
    Object.assign(overlay.style, {
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      left: 0,
      backgroundColor: 'rgba(0,0,0,0.4)',
      zIndex: 1040,
      display: 'none'
    });
    document.body.appendChild(overlay);
  }

  // 🔹 توابع باز و بسته کردن منو
  const openSidebar = () => {
    sidebar.classList.add('show');
    overlay.style.display = 'block';
    menuToggle.classList.add('active');
  };

  const closeSidebar = () => {
    sidebar.classList.remove('show');
    overlay.style.display = 'none';
    menuToggle.classList.remove('active');
  };

  // 🔹 کنترل کلیک روی آیکون منو و روی overlay
  if (menuToggle && sidebar && overlay) {
    menuToggle.addEventListener('click', () => {
      sidebar.classList.contains('show') ? closeSidebar() : openSidebar();
    });

    overlay.addEventListener('click', closeSidebar);
  }

  // 🔹 مدیریت سبد خرید
  const showCart = () => {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const cartItemsContainer = document.getElementById("cart-items");
    const totalPriceElem = document.getElementById("total-price");
    const cartCountElems = document.querySelectorAll("#cart-count, #sidebar-cart-count");

    if (!cartItemsContainer || !totalPriceElem || cartCountElems.length === 0) return;

    cartItemsContainer.innerHTML = "";

    if (cart.length === 0) {
      cartItemsContainer.innerHTML = "<p>سبد خرید خالی است.</p>";
      totalPriceElem.textContent = "مبلغ کل: ۰ تومان";
      cartCountElems.forEach(el => (el.textContent = "0"));
      return;
    }

    let totalPrice = 0;
    let totalCount = 0;

    cart.forEach(item => {
      totalPrice += item.price * item.quantity;
      totalCount += item.quantity;

      const div = document.createElement("div");
      div.className = "cart-item d-flex justify-content-between align-items-center mb-2";
      div.innerHTML = `
        <span>${item.name} (تعداد: ${item.quantity})</span>
        <span>${(item.price * item.quantity).toLocaleString()} تومان</span>
      `;
      cartItemsContainer.appendChild(div);
    });

    totalPriceElem.textContent = `مبلغ کل: ${totalPrice.toLocaleString()} تومان`;
    cartCountElems.forEach(el => el.textContent = totalCount);
  };

  // 🔹 افزودن محصول به سبد خرید
window.addToCart = function (id, name, btn, price) {
  // ➕ افزودن به localStorage
  const cart = JSON.parse(localStorage.getItem("cart")) || [];
  const index = cart.findIndex(item => item.id === id);

  if (index !== -1) {
    cart[index].quantity += 1;
  } else {
    cart.push({ id, name, price, quantity: 1 });
  }

  localStorage.setItem("cart", JSON.stringify(cart));
  showCart();

  if (btn) {
    btn.textContent = "✅ اضافه شد";
    setTimeout(() => {
      btn.textContent = "🛒 افزودن به سبد خرید";
    }, 1500);
  }

  // ➕ ارسال به سرور (در صورت نیاز)
  fetch('/api/cart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id })
  })
  .then(response => response.json())
  .then(data => {
    console.log("📡 پاسخ سرور:", data.message);
  })
  .catch(err => {
    console.warn("⚠️ خطا در ارسال به سرور:", err);
  });
};


  // 🔹 انجام پرداخت (شبیه‌سازی شده)
  window.checkout = function () {
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    if (cart.length === 0) {
      alert("سبد خرید خالی است!");
      return;
    }

    alert("✅ پرداخت انجام شد");
    localStorage.removeItem("cart");
    showCart();
  };

  // 🔹 بارگذاری اولیه سبد خرید
  showCart();
});







