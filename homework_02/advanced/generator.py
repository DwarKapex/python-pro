"""
TODO:

`gen` is a generator that yields a integer, and can accept a string sent to it.
It does not return anything.
"""

from collections.abc import Generator
from typing import assert_type  # for example


def gen() -> Generator[int, str, None]:
    """You don't need to implement it"""
    ...


# Examples


generator = gen()
assert_type(next(generator), int)
generator.send("sss")
# generator.send(3)  # expect-type-error
