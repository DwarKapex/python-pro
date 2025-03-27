from infrastructure.database import DATABASE_URL


class TestDatabase:
    def test_availability(self):
        assert DATABASE_URL.startswith("sqlite://")
