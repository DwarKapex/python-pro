from domain.models import Product
from domain.repositories import OrderRepository, ProductRepository
from domain.services import WarehouseService
from pytest_mock import MockerFixture


class TestService:
    def test_create_product(self, mocker: MockerFixture):
        mock_product_repo = mocker.Mock(spec=ProductRepository)
        mock_order_repo = mocker.Mock(spec=OrderRepository)
        service = WarehouseService(mock_product_repo, mock_order_repo)

        product = service.create_product(name="Test Product", quantity=10, price=100.0)

        assert product.name == "Test Product"
        assert product.quantity == 10
        assert product.price == 100.0
        mock_product_repo.add.assert_called_once_with(product)

    def test_create_order(self, mocker: MockerFixture):
        mock_product_repo = mocker.Mock(spec=ProductRepository)
        mock_order_repo = mocker.Mock(spec=OrderRepository)
        service = WarehouseService(mock_product_repo, mock_order_repo)

        product1 = Product(id=1, name="Product 1", quantity=5, price=50.0)
        product2 = Product(id=2, name="Product 2", quantity=10, price=100.0)
        products = [product1, product2]

        order = service.create_order(products=products)

        assert order.products == products
        mock_order_repo.add.assert_called_once_with(order)
