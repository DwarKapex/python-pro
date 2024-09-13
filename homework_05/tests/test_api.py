import datetime
import hashlib

import pytest

from src import api, store


class TestAPI:

    def setup_method(self):
        self.context = {}
        self.headers = {}
        self.settings = {}
        self.store = store.Store()

    def teardown_method(self):
        pass

    def get_response(self, request):
        return api.method_handler(
            request={"body": request, "headers": self.headers},
            ctx=self.context,
            store=self.store,
        )

    def set_valid_auth(self, request):
        if request.get("login") == api.ADMIN_LOGIN:
            request["token"] = hashlib.sha512(
                (datetime.datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).encode(
                    "utf-8"
                )
            ).hexdigest()
        else:
            msg = (
                request.get("account", "") + request.get("login", "") + api.SALT
            ).encode("utf-8")
            request["token"] = hashlib.sha512(msg).hexdigest()

    def test_empty_request(self):
        _, code = self.get_response({})
        assert api.INVALID_REQUEST == code

    @pytest.mark.parametrize(
        "rqst",
        [
            {
                "account": "horns&hoofs",
                "login": "h&f",
                "method": "online_score",
                "token": "",
                "arguments": {},
            },
            {
                "account": "horns&hoofs",
                "login": "h&f",
                "method": "online_score",
                "token": "sdd",
                "arguments": {},
            },
            {
                "account": "horns&hoofs",
                "login": "admin",
                "method": "online_score",
                "token": "",
                "arguments": {},
            },
        ],
    )
    def test_bad_auth(self, rqst):
        _, code = self.get_response(rqst)
        assert api.FORBIDDEN == code

    @pytest.mark.parametrize(
        "rqst",
        [
            {
                "account": "horns&hoofs",
                "login": "h&f",
                "method": "online_score",
                "arguments": {},
            },
        ],
    )
    def test_good_auth(self, rqst):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        rqst = {
            "account": "horns&hoofs",
            "login": "admin",
            "method": "online_score",
            "arguments": arguments,
        }
        self.set_valid_auth(rqst)
        _, code = self.get_response(rqst)
        assert api.OK == code

    @pytest.mark.parametrize(
        "rqst",
        [
            {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
            {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
            {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
        ],
    )
    def test_invalid_method_request(self, rqst):
        self.set_valid_auth(rqst)
        response, code = self.get_response(rqst)
        assert api.INVALID_REQUEST == code
        assert len(response) > 0

    @pytest.mark.parametrize(
        "arguments",
        [
            {},
            {"phone": "79175002040"},
            {"phone": "89175002040", "email": "stupnikov@otus.ru"},
            {"phone": "79175002040", "email": "stupnikovotus.ru"},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
            {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "18900101",
            },
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "XXX",
            },
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "20000101",
                "first_name": 1,
            },
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "01.01.2000",
                "first_name": "s",
                "last_name": 2,
            },
            {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
            {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
        ],
    )
    def test_invalid_score_request(self, arguments):
        request = {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "arguments": arguments,
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.INVALID_REQUEST == code
        assert len(response) > 0

    @pytest.mark.parametrize(
        "arguments",
        [
            {"phone": "79175002040", "email": "stupnikov@otus.ru"},
            {"phone": 79175002040, "email": "stupnikov@otus.ru"},
            {
                "gender": 1,
                "birthday": "20000101",
                "first_name": "a",
                "last_name": "b",
            },
            {"gender": 0, "birthday": "20000101"},
            {"gender": 2, "birthday": "20000101"},
            {"first_name": "a", "last_name": "b"},
            {
                "phone": "79175002040",
                "email": "stupnikov@otus.ru",
                "gender": 1,
                "birthday": "20000101",
                "first_name": "a",
                "last_name": "b",
            },
        ],
    )
    def test_ok_score_request(self, mocker, arguments):
        request = {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "online_score",
            "arguments": arguments,
        }
        self.set_valid_auth(request)
        mocker.patch("src.store.Store.cache_get", return_value=5)
        response, code = self.get_response(request)
        assert api.OK == code
        score = response.get("score")
        assert isinstance(score, (int, float)) and score >= 0
        assert sorted(self.context["has"]) == sorted(arguments.keys())

    def test_ok_score_admin_request(self):
        arguments = {"phone": "79175002040", "email": "stupnikov@otus.ru"}
        request = {
            "account": "horns&hoofs",
            "login": "admin",
            "method": "online_score",
            "arguments": arguments,
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.OK == code
        score = response.get("score")
        assert score == 42

    @pytest.mark.parametrize(
        "arguments",
        [
            {},
            {"date": "20170720"},
            {"client_ids": [], "date": "20170720"},
            {"client_ids": {1: 2}, "date": "20170720"},
            {"client_ids": ["1", "2"], "date": "20170720"},
            {"client_ids": [1, 2], "date": "XXX"},
        ],
    )
    def test_invalid_interests_request(self, arguments):
        request = {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "clients_interests",
            "arguments": arguments,
        }
        self.set_valid_auth(request)
        response, code = self.get_response(request)
        assert api.INVALID_REQUEST == code
        assert len(response) > 0

    @pytest.mark.parametrize(
        "arguments",
        [
            # {
            #     "client_ids": [1, 2, 3],
            #     "date": datetime.datetime.today().strftime("%Y%m%d"),
            # },
            {"client_ids": [1, 2], "date": "20170908"},
            # {"client_ids": [0]},
        ],
    )
    def test_ok_interests_request(self, mocker, arguments):
        request = {
            "account": "horns&hoofs",
            "login": "h&f",
            "method": "clients_interests",
            "arguments": arguments,
        }
        self.set_valid_auth(request)
        mocker.patch("src.store.Store.get", return_value='{"score": 2}')
        response, code = self.get_response(request)
        assert api.OK == code
        assert len(arguments["client_ids"]) == len(response)

        assert all(
            v and all(isinstance(i, (bytes, str)) for i in v) for v in response.values()
        )
        assert self.context.get("nclients") == len(arguments["client_ids"])
