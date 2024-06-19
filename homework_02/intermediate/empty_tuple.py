"""
TODO:

foo should accept a empty tuple argument.
"""

from typing import Tuple


def foo(x: Tuple):
    pass


# Alternative solution
# def foo(x: tuple[()]):
#     pass


# Examples
foo(())
# foo((1))  # expect-type-error
