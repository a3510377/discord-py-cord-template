from typing import Optional, Any


def get(
    locals: str,
    key: str,
    default: Optional[str] = None,
    *,
    lang: str,
    **kwargs: Any,
) -> Optional[str]:
    ...
