"""
TODO:

The function `add` accepts one argument and returns a value, they
all have the same type. The type can only be int or subclasses of int.
"""

# For Python < 3.12
from typing import assert_type  # for examples
from typing import TypeVar

T = TypeVar("T", bound=int)


def add(a: T) -> T:
    return a


# For Python >= 3.12
# def add[T: int](a: T) -> T:
#     return a


# Examples


class MyInt(int):
    pass


assert_type(add(1), int)
assert_type(add(MyInt(1)), MyInt)
# assert_type(add("1"), str)  # expect-type-error
# add(["1"], ["2"])  # expect-type-error
# add("1", 2)  # expect-type-error
