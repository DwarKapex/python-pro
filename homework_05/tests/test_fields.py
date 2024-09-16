import pytest

from src import api


class TestFields:
    @pytest.mark.parametrize(
        "nullable, required, arguments, expected_response, expected_code",
        [
            (True, False, {}, None, api.OK),
            (
                False,
                True,
                {},
                "Field <first_name> is not available",
                api.INVALID_REQUEST,
            ),
        ],
    )
    def test_char_field(
        self, nullable, required, arguments, expected_response, expected_code
    ):
        first_name = api.CharField(required, nullable)
        request = {
            "account": "horns&hoofs",
            "login": "admin",
            "method": "online_score",
            "arguments": arguments,
        }
        response, code = first_name.validate(request, "first_name")
        assert response == expected_response
        assert code == expected_code

    @pytest.mark.parametrize(
        "nullable, required, arguments, expected_response, expected_code",
        [
            (True, False, {}, None, api.OK),
            (False, True, {"phone": "79871234123"}, None, api.OK),
            (
                False,
                True,
                {"phone": "19871234"},
                "Phone number length must be 11, but got 8",
                api.INVALID_REQUEST,
            ),
        ],
    )
    def test_phone_field(
        self, nullable, required, arguments, expected_response, expected_code
    ):
        phone = api.PhoneField(nullable=nullable, required=required)
        response, code = phone.validate(arguments, "phone")
        assert response == expected_response
        assert code == expected_code
