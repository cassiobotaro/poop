"""Tests that POOP type bindings are mangled, not publicly visible.

Lowercase Python builtins (`int`, `list`, ...) are rewritten at parse time
to the mangled `_poop_*` name so `x.is_instance(int)` works. The mangled
names live in the namespace; the PascalCase ones do not, keeping the
user-facing globals limited to true entry points (`Try`, `Path`, `With`).
"""

import pytest

from poop import Interpreter
from poop.transformers import DEFAULT_NAMESPACE
from poop.types.block import Block
from poop.types.boolean import Boolean
from poop.types.byte_array import ByteArray
from poop.types.bytes import Bytes
from poop.types.complex import Complex
from poop.types.dict import Dict
from poop.types.enumerate import Enumerate
from poop.types.float import Float
from poop.types.frozen_set import FrozenSet
from poop.types.int import Int
from poop.types.list import List
from poop.types.memory_view import MemoryView
from poop.types.object import Object
from poop.types.range import Range
from poop.types.set import Set
from poop.types.slice import Slice
from poop.types.string import Str
from poop.types.tuple import Tuple
from poop.types.zip import Zip


def _eval(source: str) -> object:
    interpreter = Interpreter()
    tree = interpreter.transform_source(f"result = {source}")
    ns = dict(DEFAULT_NAMESPACE)
    exec(compile(tree, "<test>", "exec"), ns)  # noqa: S102
    return ns["result"]


@pytest.mark.parametrize(
    ("mangled", "type_"),
    [
        ("_poop_boolean", Boolean),
        ("_poop_str", Str),
        ("_poop_int", Int),
        ("_poop_float", Float),
        ("_poop_list_cls", List),
        ("_poop_tuple_cls", Tuple),
        ("_poop_dict", Dict),
        ("_poop_set_cls", Set),
        ("_poop_frozenset", FrozenSet),
        ("_poop_bytes", Bytes),
        ("_poop_bytearray", ByteArray),
        ("_poop_memoryview", MemoryView),
        ("_poop_complex", Complex),
        ("_poop_range_cls", Range),
        ("_poop_enumerate_cls", Enumerate),
        ("_poop_zip_cls", Zip),
        ("_poop_block", Block),
        ("_poop_object", Object),
        ("_poop_slice", Slice),
    ],
)
def test_mangled_type_binding_is_in_default_namespace(
    mangled: str, type_: type
) -> None:
    assert DEFAULT_NAMESPACE[mangled] is type_


@pytest.mark.parametrize(
    "pascal",
    [
        "Boolean",
        "Str",
        "Int",
        "Float",
        "List",
        "Tuple",
        "Dict",
        "Set",
        "FrozenSet",
        "Bytes",
        "ByteArray",
        "MemoryView",
        "Complex",
        "Range",
        "Enumerate",
        "Zip",
        "Block",
        "Object",
        "Slice",
        "Map",
        "Filter",
    ],
)
def test_pascal_type_name_is_not_in_default_namespace(pascal: str) -> None:
    assert pascal not in DEFAULT_NAMESPACE


@pytest.mark.parametrize(
    ("literal", "lowercase"),
    [
        ('"hi"', "str"),
        ("(42)", "int"),
        ("(3.14)", "float"),
        ("True", "bool"),
        ("[1]", "list"),
        ("(1,)", "tuple"),
        ("{1: 2}", "dict"),
        ("{1, 2}", "set"),
    ],
)
def test_is_instance_lowercase_name_resolves_to_poop_type(
    literal: str, lowercase: str
) -> None:
    assert bool(_eval(f"{literal}.is_instance({lowercase})")) is True
