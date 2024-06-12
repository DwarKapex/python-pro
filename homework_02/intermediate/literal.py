"""
TODO:

foo only accepts literal 'left' and 'right' as its argument.
"""

from typing import Literal


def foo(direction: Literal["left", "right"]): ...


# Examples
foo("left")
foo("right")

a = "".join(["l", "e", "f", "t"])
# foo(a)  # expect-type-error
