# flake8: noqa
from domain.models import Order, Product
from infrastructure.orm import OrderORM, ProductORM
from infrastructure.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyProductRepository,
)
from pytest_mock import MockerFixture
from sqlalchemy.orm import Session


class TestRepository:
    def test_sqlalchemy_product_repository_add(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        repo = SqlAlchemyProductRepository(mock_session)
        product = Product(id=1, name="Test Product", quantity=10, price=100)

        repo.add(product)

        mock_session.add.assert_called_once()
        added_product_orm = mock_session.add.call_args[0][0]
        assert isinstance(added_product_orm, ProductORM)
        assert added_product_orm.name == "Test Product"
        assert added_product_orm.quantity == 10
        assert added_product_orm.price == 100

    def test_sqlalchemy_product_repository_get(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        repo = SqlAlchemyProductRepository(mock_session)
        product_orm = ProductORM(id=1, name="Test Product", quantity=10, price=100)
        mock_session.query.return_value.filter_by.return_value.one.return_value = (
            product_orm
        )

        product = repo.get(1)

        mock_session.query.assert_called_once_with(ProductORM)
        assert product.id == 1
        assert product.name == "Test Product"
        assert product.quantity == 10
        assert product.price == 100

    def test_sqlalchemy_product_repository_list(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        repo = SqlAlchemyProductRepository(mock_session)
        products_orm = [
            ProductORM(id=1, name="Product 1", quantity=10, price=100),
            ProductORM(id=2, name="Product 2", quantity=20, price=200),
        ]
        mock_session.query.return_value.all.return_value = products_orm

        products = repo.list()

        mock_session.query.assert_called_once_with(ProductORM)
        assert len(products) == 2
        assert products[0].id == 1
        assert products[1].id == 2

    def test_sqlalchemy_order_repository_add(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        repo = SqlAlchemyOrderRepository(mock_session)
        product1 = Product(id=1, name="Product 1", quantity=10, price=100)
        product2 = Product(id=2, name="Product 2", quantity=20, price=200)
        order = Order(id=42, products=[product1, product2])

        product_orm1 = ProductORM(id=1, name="Product 1", quantity=10, price=100)
        product_orm2 = ProductORM(id=2, name="Product 2", quantity=20, price=200)

        mock_session.query.return_value.filter_by.return_value.one.side_effect = [
            product_orm1,
            product_orm2,
        ]

        repo.add(order)

        mock_session.add.assert_called_once()
        added_order_orm = mock_session.add.call_args[0][0]
        assert isinstance(added_order_orm, OrderORM)
        assert len(added_order_orm.products) == 2
        assert added_order_orm.products[0] == product_orm1
        assert added_order_orm.products[1] == product_orm2

    def test_sqlalchemy_order_repository_get(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        repo = SqlAlchemyOrderRepository(mock_session)
        product_orm1 = ProductORM(id=1, name="Product 1", quantity=10, price=100)
        product_orm2 = ProductORM(id=2, name="Product 2", quantity=20, price=200)
        order_orm = OrderORM(id=1, products=[product_orm1, product_orm2])
        mock_session.query.return_value.filter_by.return_value.one.return_value = (
            order_orm
        )

        order = repo.get(1)

        mock_session.query.assert_called_once_with(OrderORM)
        assert order.id == 1
        assert len(order.products) == 2
        assert order.products[0].id == 1
        assert order.products[1].id == 2

    def test_sqlalchemy_order_repository_list(self, mocker: MockerFixture):
        mock_session = mocker.Mock(spec=Session)
        repo = SqlAlchemyOrderRepository(mock_session)
        product_orm1 = ProductORM(id=1, name="Product 1", quantity=10, price=100)
        product_orm2 = ProductORM(id=2, name="Product 2", quantity=20, price=200)
        order_orm1 = OrderORM(id=1, products=[product_orm1, product_orm2])
        order_orm2 = OrderORM(id=2, products=[product_orm1])
        mock_session.query.return_value.all.return_value = [order_orm1, order_orm2]

        orders = repo.list()

        mock_session.query.assert_called_once_with(OrderORM)
        assert len(orders) == 2
        assert orders[0].id == 1
        assert len(orders[0].products) == 2
        assert orders[1].id == 2
        assert len(orders[1].products) == 1
