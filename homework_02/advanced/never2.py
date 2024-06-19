from typing import assert_never  # for example
from typing import Never


def stop() -> Never:
    """TODO: implement this function to make it type check"""
    raise RuntimeError("never return")


# Examples
assert_never(stop())
