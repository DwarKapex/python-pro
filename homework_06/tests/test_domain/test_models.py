from domain.models import Order, Product


class TestModels:
    def test_product_creation(self):
        product = Product(id=1, name="Test Product", quantity=10, price=100.0)
        assert product.id == 1
        assert product.name == "Test Product"
        assert product.quantity == 10
        assert product.price == 100.0

    def test_order_creation_empty_products(self):
        order = Order(id=1)
        assert order.id == 1
        assert order.products == []

    def test_order_creation_with_products(self):
        product1 = Product(id=1, name="Product 1", quantity=5, price=50.0)
        product2 = Product(id=2, name="Product 2", quantity=10, price=100.0)
        order = Order(id=1, products=[product1, product2])
        assert order.id == 1
        assert order.products == [product1, product2]

    def test_order_add_product(self):
        order = Order(id=1)
        product = Product(id=1, name="Test Product", quantity=10, price=100.0)
        order.add_product(product)
        assert order.products == [product]

    def test_order_add_multiple_products(self):
        order = Order(id=1)
        product1 = Product(id=1, name="Product 1", quantity=5, price=50.0)
        product2 = Product(id=2, name="Product 2", quantity=10, price=100.0)
        order.add_product(product1)
        order.add_product(product2)
        assert order.products == [product1, product2]

    def test_order_add_product_mutability(self):
        order = Order(id=1)
        product = Product(id=1, name="Test Product", quantity=10, price=100.0)
        order.add_product(product)
        assert len(order.products) == 1
        order.add_product(product)
        assert len(order.products) == 2
        assert order.products == [product, product]
