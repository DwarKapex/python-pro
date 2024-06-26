"""
TODO:

The function `add` accepts two arguments and returns a value, they all have
the same type.
"""

from typing import List, TypeVar, assert_type  # for examples

T = TypeVar("T")


def add(a: T, b: T) -> T:
    return a


"""
TODO:

The function `add` accepts two arguments and returns a value, they
all have the same type.
"""

# Before 3.12 you have to write
# from typing import TypeVar
#
# T = TypeVar("T")
#
#
# def add(a: T, b: T) -> T:
#     return a


# For Python >= 3.12
# def add[T](a: T, b: T) -> T:
#     return a


# Examples

assert_type(add(1, 2), int)
assert_type(add("1", "2"), str)
assert_type(add(["1"], ["2"]), List[str])
# assert_type(add(1, "2"), int)  # expect-type-error
