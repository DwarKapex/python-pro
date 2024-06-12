"""
TODO:

foo should return an integer argument.
"""

from typing import assert_type  # for example


def foo() -> int:
    return 1


# Example

assert_type(foo(), int)
# assert_type(foo(), str)  # expect-type-error
