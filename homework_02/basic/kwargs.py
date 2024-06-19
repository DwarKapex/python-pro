"""
TODO:

`foo` takes keyword arguments of type integer or string.
"""

from typing import Union


def foo(**kwargs: Union[str, int]): ...


# Alternative solution
# def foo(**kwargs: int | str):
#     ...


# Examples
foo(a=1, b="2")
# foo(a=[1])  # expect-type-error
