"""
TODO:

`run_async` takes an awaitable integer.
"""

from asyncio import Queue  # for example
from typing import Awaitable

# typing.Awaitable was deprecated in python3.8
# use collection.abc.Awaitable instead


def run_async(x: Awaitable[int]): ...


# Alternative solution
#
# from collections.abc import Awaitable
#
#
# def run_async(func: Awaitable[int]):
#     ...


# Examples

queue: Queue[int] = Queue()
queue2: Queue[str] = Queue()


async def async_function() -> int:
    return await queue.get()


async def async_function2() -> str:
    return await queue2.get()


run_async(async_function())
# run_async(1)  # expect-type-error
# run_async(async_function2())  # expect-type-error
