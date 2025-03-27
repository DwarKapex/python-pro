from infrastructure.orm import OrderORM, ProductORM


class TestORM:
    def test_successful_creation(self):
        ProductORM()
        OrderORM()
