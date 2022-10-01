import inspect
from typing import Any, Callable, Optional, TypeVar


__all__ = (
    "fix_doc",
    "has_value",
    "set_dict_default",
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


def set_dict_default(
    value: T,
    key: str,
    default: Any,
    *,
    check: Optional[Callable[[T], bool]] = None,
) -> T:
    is_dict = False
    check_key = None

    try:
        if isinstance(value, dict):
            is_dict = True
            check_key = value[key]
        else:
            check_key = value.__dict__[key]
    except KeyError:
        pass

    if not has_value(check_key, check=check):
        if is_dict:
            value[key] = default
        else:
            value.__dict__[key] = default

    return value
