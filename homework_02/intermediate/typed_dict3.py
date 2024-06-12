"""
TODO:

Define a class `Person` that represents a dictionary with five string keys:
    name, age, gender, address, email

The value of each key must be the specified type:
    name - str, age - int, gender - str, address - str, email - str

Note: Only `name` is required
"""

from typing import Required, TypedDict


class Person(TypedDict, total=False):
    name: Required[str]
    age: int
    gender: str
    address: str
    email: str


# Alternative solution:
# Person = TypedDict('Person', {
#     name: Required[str],
#     age: int,
#     gender: str,
#     address: str,
#     email: str,
# }, total=False):

# Examples
a: Person = {
    "name": "Capy",
    "age": 1,
    "gender": "Male",
    "address": "earth",
    "email": "capy@bara.com",
}

b: Person = {"name": "Capy"}
# expect-type-error
# a: Person = {"age": 1, "gender": "Male", "address": "", "email": ""}
