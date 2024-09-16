#!/usr/bin/env python

import collections
import datetime
import hashlib
import inspect
import json
import logging
import numbers
import uuid
from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List, Tuple, Union

from . import common, scoring, store

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}


class RequiredNullable:
    required = False
    nullable = False

    def __init__(self, required, nullable=False):
        self.required = required
        self.nullable = nullable
        self._value = None

    def validate(
        self, request: Dict[str, Union[str, Dict]], validate_args
    ) -> Tuple[str | None, int]:
        response, code = self.validate_require_nullable(request, validate_args)
        if code != OK:
            return response, code
        if request.get(validate_args, None) is not None:
            response, code = self.validate_value(request.get(validate_args, None))
        if code != OK:
            return response, code
        self._value = request.get(validate_args, None)
        return None, OK

    def validate_require_nullable(
        self, request: Dict[str, Union[str, Dict]], validate_args
    ) -> Tuple[str | None, int]:
        if not self.required:
            return None, OK
        logging.debug("Validating arg: %s", validate_args)
        if validate_args not in request:
            return f"Field <{validate_args}> is not available", INVALID_REQUEST
        if len(request[validate_args]) == 0 and not self.nullable:
            return f"Field <{validate_args}> must not be empty", INVALID_REQUEST
        return None, OK

    def validate_value(self, value) -> Tuple[str | None, int]:
        # pylint: disable=unused-argument
        return None, OK


class CharField(RequiredNullable):
    def __eq__(self, other) -> bool:
        return self._value == str(other)

    def __add__(self, other):
        return str(self) + str(other)

    def __str__(self):
        return self._value

    def __bool__(self):
        return self._value is not None

    def validate_value(self, value) -> Tuple[str | None, int]:
        if value is None:
            return None, OK
        if not isinstance(value, str):
            return (
                f"Wrong field type: expected <str>, received <{type(value)}>",
                INVALID_REQUEST,
            )
        return None, OK


class ArgumentsField(RequiredNullable):
    def validate_value(self, value) -> Tuple[str | None, int]:
        if not isinstance(value, dict):
            return (
                f"Invalid arguments type: expected <dict>, received {type(value)}",
                INVALID_REQUEST,
            )
        return None, OK

    def get_value(self) -> Dict:
        if not self._value:
            return {}
        return self._value

    def __contains__(self, item) -> bool:
        if self._value:
            return item in self._value
        return False


class EmailField(RequiredNullable):
    def validate_value(self, value) -> Tuple[str | None, int]:
        if "@" not in value:
            return "Invalid email: email must contain <@>", INVALID_REQUEST
        return None, OK


class PhoneField(RequiredNullable):
    def validate_value(self, value: Union[str, int]) -> Tuple[str | None, int]:
        if not isinstance(value, int) and not isinstance(value, str):
            return (
                f"Unsupported value for phone number: expect <str | int>, got {type(value)}",
                INVALID_REQUEST,
            )
        value = str(value)
        if len(value) == 0:
            return None, OK
        if len(value) != 11:
            return (
                f"Phone number length must be 11, but got {len(value)}",
                INVALID_REQUEST,
            )
        if not value.startswith("7"):
            return (
                f"Phone number must start with 7, but starts with {value[0]}",
                INVALID_REQUEST,
            )

        return None, OK


class DateField(RequiredNullable):
    max_diff_days: float = 0.0

    def validate_value(self, value) -> Tuple[str | None, int]:
        if value is None:
            return None, OK
        try:
            datetime_obj = datetime.datetime.strptime(value, "%Y%m%d")
        except ValueError as val:
            return f"Invalid date: {val}", INVALID_REQUEST

        if self.max_diff_days:
            now = datetime.datetime.now()
            if (now - datetime_obj).days > self.max_diff_days:
                return (
                    f"The date is too far in the past: expected max diff {self.max_diff_days} days",
                    INVALID_REQUEST,
                )
        return None, OK


class BirthDayField(DateField):
    max_diff_days: float = 70 * 365.25  # 70 years


class GenderField(RequiredNullable):
    def validate_value(self, value) -> Tuple[str | None, int]:
        if value is None:
            return None, OK
        if not isinstance(value, int):
            return "Gender field must be int", INVALID_REQUEST
        if value < 0 or value > 2:
            return "Gender field must be 0, 1 or 2", INVALID_REQUEST

        return None, OK


class ClientIDsField(RequiredNullable):
    def validate_value(self, value: List | Tuple) -> Tuple[str | None, int]:
        if not isinstance(value, collections.abc.Sequence) or len(value) == 0:
            return (
                f"CliendIDsField type is incorrect: expect <array of numbers>, got {type(value)}",
                INVALID_REQUEST,
            )
        for item in value:
            if not isinstance(item, numbers.Number):
                return (
                    f"CliendIDsField type is incorrect: expect <array of numbers>,"
                    f" got {type(item)} for one of them",
                    INVALID_REQUEST,
                )
        return None, OK


class CommonRequest:
    # pylint: disable=too-few-public-methods
    def __init__(self, arguments):
        self._arguments = arguments

    def validate(self):
        final_response = ""
        final_code = OK
        for field, method in inspect.getmembers(self):
            if not field.startswith("_") and not inspect.ismethod(method):
                logging.debug("ClientsInterestsRequest: validate field: %s", field)
                field_to_validate = getattr(self, field)
                response, code = field_to_validate.validate(
                    self._arguments.get_value(), field
                )
                logging.debug("Received response: %s, code: %d", response, code)
                if code != OK:
                    final_code = INVALID_REQUEST
                    final_response += response + ", "
                    logging.debug("Final response so far: %s", final_response)

        return final_response, final_code


class ClientsInterestsRequest(CommonRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def evaluate(self, store, ctx):
        cliends_ids = self._arguments.get_value()["client_ids"]
        result = {cid: scoring.get_interests(store, cid) for cid in cliends_ids}
        ctx["nclients"] = len(cliends_ids)
        return result, OK


class OnlineScoreRequest(CommonRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        final_response = ""
        final_code = OK
        # check presents of the pairs:
        #   phone - email,
        #   first name - last name
        #   gender - birthday
        pairs = [
            ("phone", "email"),
            ("first_name", "last_name"),
            ("gender", "birthday"),
        ]
        min_arguments_availability = False
        for f, s in pairs:
            logging.debug("Check pair %s-%s", f, s)
            if f not in self._arguments or s not in self._arguments:
                logging.debug("Pair %s-%s is not in provided arguments", f, s)
            else:
                min_arguments_availability = True
                logging.debug("Preset")
                break

        if not min_arguments_availability:
            return (
                f"No pair {pairs} is in provided arguments, but should be at least one",
                INVALID_REQUEST,
            )

        for field, method in inspect.getmembers(self):
            if not field.startswith("_") and not inspect.ismethod(method):
                logging.debug("OnlineScoreRequest: validate field: %s", field)
                field_to_validate = getattr(self, field)
                response, code = field_to_validate.validate(
                    self._arguments.get_value(), field
                )
                logging.debug("Received response: %s, code: %d", response, code)
                if code != OK:
                    final_code = INVALID_REQUEST
                    final_response += response + ", "
                    logging.debug("Final response so far: %s ", final_response)

        return final_response, final_code

    def evaluate(self, is_admin, store, ctx):
        logging.debug("Start OnlineScore evaluation")
        score = (
            42 if is_admin else scoring.get_score(store, **self._arguments.get_value())
        )
        ctx["has"] = self._arguments.get_value().keys()
        return {"score": score}, OK


class MethodRequest:
    account = CharField(required=True, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    _method_binder = {
        "online_score": OnlineScoreRequest,
        "clients_interests": ClientsInterestsRequest,
    }

    def __init__(self, request: Dict[str, Union[str, Dict]]):
        self._request = request

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN

    def validate_request(self) -> Tuple[str | None, int]:
        final_response = ""
        final_code = OK
        for field, method in inspect.getmembers(self):
            if "_" not in field and not inspect.ismethod(method):
                logging.debug("Validate field: %s", field)
                a = getattr(self, field)
                response, code = a.validate(self._request, field)
                logging.debug("Recieved response: %s, code: %d", response, code)
                if code != OK:
                    final_code = INVALID_REQUEST
                    final_response += response + ", "
                    logging.debug("Final response so far: %s", final_response)

        if final_code == OK and not check_auth(self):
            logging.debug("Checking authentication")
            logging.debug(
                "Final code %s, check_auth result %s", final_code, check_auth(self)
            )
            return "Forbidden", FORBIDDEN

        response, code = self.validate_method()
        if code != OK:
            final_code = INVALID_REQUEST
            final_response += response + ", "
            logging.debug("Final response so far: %s ", final_response)

        return final_response if final_response else None, final_code

    def validate_method(self) -> Tuple[str | None, int]:
        if not self.method:
            return "Invalid method", INVALID_REQUEST
        logging.debug("Validating method <%s>", self._method_binder[str(self.method)])
        method = self._method_binder[str(self.method)](self.arguments)
        return method.validate()  # type: ignore

    def evaluate_method(self, ctx, store):
        logging.debug("Evaluating method %s", self._method_binder[str(self.method)])
        method_args = {"store": store, "ctx": ctx}
        if str(self.method) == "online_score":
            method_args["is_admin"] = self.is_admin
        method = self._method_binder[str(self.method)](self.arguments)
        return method.evaluate(**method_args)


def check_auth(request):
    logging.debug("Start auth check")
    if request.is_admin:
        digest = hashlib.sha512(
            (datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode("utf-8")
        ).hexdigest()
    else:
        digest = hashlib.sha512(
            (request.account + request.login + SALT).encode("utf-8")
        ).hexdigest()
    logging.debug("Digest = %s, token = %s", digest, request.token)
    return digest == request.token


def validate_request(request: Dict[str, Union[str, Dict]]):
    method_request = MethodRequest(request.get("body", {}))  # type: ignore
    logging.info("Start request validation")
    response, code = method_request.validate_request()
    logging.info(
        "Complete validation results with response: %s, code: %d", response, code
    )
    if code != OK:
        return response, code, None
    logging.info("Start scoring with method: %s", request["body"].get("method", None))  # type: ignore
    logging.info("Start method validation")
    response, code = method_request.validate_method()
    return response, code, method_request


def method_handler(
    request: Dict[str, Union[str, Dict]], ctx: Dict[str, Union[str, int]], store
) -> Tuple[str | None, int]:
    logging.info("Call method_handler with request %s: ", request)
    response, code, method = validate_request(request)
    if code == OK:
        logging.debug("Start method evaluation")
        response, code = method.evaluate_method(ctx, store)
        logging.debug("Context: %s", ctx)
    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {"method": method_handler}
    store = store.Store()

    def get_request_id(self, headers):
        return headers.get("HTTP_X_REQUEST_ID", uuid.uuid4().hex)

    # pylint: disable=invalid-name
    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers["Content-Length"]))
            request = json.loads(data_string)
        except ValueError:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s", self.path, data_string, context["request_id"])
            if path in self.router:
                try:
                    response, code = self.router[path](
                        {"body": request, "headers": self.headers}, context, self.store
                    )
                # pylint: disable=broad-exception-caught)
                except Exception as e:
                    logging.exception("Unexpected error: %s", e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode("utf-8"))


def parse_arguments():
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=8080)
    parser.add_argument("-l", "--log", action="store", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    common.configure_logging()
    server = HTTPServer(("localhost", args.port), MainHTTPHandler)
    logging.info("Starting server at %s", args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
