"""
TODO:

Define a generic class that represents a stack.
It can be instantiated with a certain type, with method `push`
accepting an object of the specified type, and `pop` returning
an an object of the same type
"""

# Before Python 3.12
from typing import assert_type  # for example
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self.items = []

    def push(self, item: T) -> None:
        self.items.append(item)

    def pop(self) -> T:
        return self.items.pop()


# For Python>=3.12
# class Stack[T]:
#     def __init__(self) -> None:
#         self.items: list[T] = []
#
#     def push(self, item: T) -> None:
#         self.items.append(item)
#
#     def pop(self) -> T:
#         return self.items.pop()


# Example #

s = Stack[int]()
s.push(1)
assert_type(s.pop(), int)
# s.push("foo")  # expect-type-error
# assert_type(s.pop(), str)  # expect-type-error
