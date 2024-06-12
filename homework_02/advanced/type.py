"""
TODO:

`make_object` takes a class returns an instance of it.
"""

from typing import Type


def make_object(cls: Type) -> Type:
    return cls()


# Alternative solution
# from typing import Any
#
#
# def make_object(cls: type[Any]):
#     return cls()


# Example
class MyClass:
    pass


def f():
    pass


c = make_object(MyClass)
c = make_object(int)
# c = make_object(f)  # expect-type-error
# c = make_object("sss")  # expect-type-error
# c = make_object(["sss"])  # expect-type-error
