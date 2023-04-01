import inspect
from pathlib import Path
from typing import Callable, TypeVar, Union

__all__ = (
    "fix_doc",
    "has_value",
    "get_absolute_name_from_path",
)

T = TypeVar("T")


def fix_doc(*doc: str):
    return inspect.cleandoc("\n".join(doc))


def has_value(
    value: T,
    *,
    check: Callable[[T], bool] = lambda x: x is None,
) -> bool:
    return not ((check is None and value is None) or (check and check(value)))


def get_absolute_name_from_path(filename: Union[str, Path]) -> str:
    from bot import __config_path__

    paths = [(p := Path(filename).resolve()).stem]

    while not __config_path__.samefile(p := p.parent):
        paths.append(p.stem)

    return ".".join(reversed(paths))
