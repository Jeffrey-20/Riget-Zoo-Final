
from decimal import Decimal
from shop.models import Product
from shop.models import Product, Order, OrderItem
import random, string

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id, quantity=1):
        product_id = str(product_id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}
        self.cart[product_id]['quantity'] += quantity
        self.save()

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            item = self.cart[str(product.id)]
            item['product'] = product
            item['total_price'] = Decimal(product.price) * item['quantity']
            yield item

    def clear(self):
        del self.session['cart']
        self.save()

    def get_total_price(self):
        return sum(Decimal(item['product'].price) * item['quantity'] for item in self)

    def create_order(self, user=None):
        """Convert cart into an Order with unique ID and linked OrderItems."""
        total = self.get_total_price()
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        order = Order.objects.create(
            user=user if user and user.is_authenticated else None,
            total_price=total,
            order_id=order_id
        )

        for item in self:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        self.clear()
        return order