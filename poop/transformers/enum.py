from poop.types.enum import (
    Enum,
    EnumNamespace,
    Flag,
    IntEnum,
    IntFlag,
    ReprEnum,
    StrEnum,
    auto,
)

NAMESPACE: dict[str, object] = {
    "enum": EnumNamespace,
    "Enum": Enum,
    "IntEnum": IntEnum,
    "StrEnum": StrEnum,
    "Flag": Flag,
    "IntFlag": IntFlag,
    "ReprEnum": ReprEnum,
    "auto": auto,
}
