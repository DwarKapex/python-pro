"""
TODO:

The function `add` accepts two arguments and returns a value, they all
have the same type. The type can only be str or int (or their subclasses).
"""

from typing import assert_type  # for examples
from typing import TypeVar

Choosable = TypeVar("Choosable", str, int)


def add(a: Choosable, b: Choosable) -> Choosable:
    return a


# For Python < 3.12
# from typing import TypeVar
#
# T = TypeVar("T", int, str)
#
#
# def add(a: T, b: T) -> T:
#     return a


# For Python >= 3.12
# def add[T: (str, int)](a: T, b: T) -> T:
#     return a


# Examples

assert_type(add(1, 2), int)
assert_type(add("1", "2"), str)

# add(["1"], ["2"])  # expect-type-error
# add("1", 2)  # expect-type-error
