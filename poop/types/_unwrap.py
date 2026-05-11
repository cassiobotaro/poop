from poop.types.none import NoneClass


def _is_absent(value: object) -> bool:
    return value is None or isinstance(value, NoneClass)


def _unwrap[T](value: object, default: T) -> T:
    if _is_absent(value):
        return default
    return getattr(value, "_value")  # noqa: B009


def _unwrap_bool(value: object, default: bool) -> bool:
    if _is_absent(value):
        return default
    return bool(value)
