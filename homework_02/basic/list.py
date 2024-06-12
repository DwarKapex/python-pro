"""
TODO:

foo should accept a list argument, whose elements are string.
"""

from typing import List


def foo(x: List[str]):
    pass


# Alternative solution
# def foo(x: list[str]):
#     pass


# Examples
foo(["foo", "bar"])
# foo(["foo", 1])  # expect-type-error
