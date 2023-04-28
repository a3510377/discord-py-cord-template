import inspect
from pathlib import Path

__all__ = (
    "fix_doc",
    "get_absolute_name_from_path",
)


def fix_doc(*doc: str):
    """
    Clean up indentation from docstrings.
    Any whitespace that can be uniformly removed from the second line
    onwards is removed.

    Parameters:
    -----------
    *doc: list[`str`]
        A doc that needs to be formatted.
    """
    return inspect.cleandoc("\n".join(doc))


def get_absolute_name_from_path(
    path: str | Path,
    base_path: str | Path | None = None,
) -> str:
    """
    Converts absolute paths to relative positions.

    Parameters:
    -----------
    path: `str` | `Path`
        The absolute path that needs to be converted.
    base_path: `str` | `Path` | None
        The primary path of the relative path.
    """
    if not base_path:
        from bot import __config_path__

        base_path = __config_path__

    paths = [(p := Path(path).resolve()).stem]

    while not Path(base_path).samefile(p := p.parent):
        paths.append(p.stem)

    return ".".join(reversed(paths))
