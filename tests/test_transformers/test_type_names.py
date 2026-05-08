"""Tests that public POOP type names are exposed in the user namespace.

Each transformer exposes both its private literal-construction binding
(`_poop_str`, `_poop_int`, ...) and a public type binding (`Str`, `Int`,
...) that user code can pass to `is_instance`. Lowercase Python builtin
names that overlap (`str`, `int`, ...) are also rewritten to the
capitalized POOP name at parse time so `x.is_instance(str)` is no longer
silently false.
"""

import pytest

from poop import Interpreter
from poop.transformers import DEFAULT_NAMESPACE
from poop.transformers.base import BaseTransformer
from poop.transformers.block import BlockTransformer
from poop.transformers.boolean import BooleanTransformer
from poop.transformers.byte_array import ByteArrayTransformer
from poop.transformers.bytes import BytesTransformer
from poop.transformers.complex import ComplexTransformer
from poop.transformers.dict import DictTransformer
from poop.transformers.enumerate import EnumerateTransformer
from poop.transformers.float import FloatTransformer
from poop.transformers.frozen_set import FrozenSetTransformer
from poop.transformers.int import IntTransformer
from poop.transformers.list import ListTransformer
from poop.transformers.memory_view import MemoryViewTransformer
from poop.transformers.range import RangeTransformer
from poop.transformers.set import SetTransformer
from poop.transformers.string import StrTransformer
from poop.transformers.tuple import TupleTransformer
from poop.transformers.zip import ZipTransformer
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
from poop.types.range import Range
from poop.types.set import Set
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
    ("transformer", "name", "type_"),
    [
        (BooleanTransformer, "Boolean", Boolean),
        (StrTransformer, "Str", Str),
        (IntTransformer, "Int", Int),
        (FloatTransformer, "Float", Float),
        (ListTransformer, "List", List),
        (TupleTransformer, "Tuple", Tuple),
        (DictTransformer, "Dict", Dict),
        (SetTransformer, "Set", Set),
        (FrozenSetTransformer, "FrozenSet", FrozenSet),
        (BytesTransformer, "Bytes", Bytes),
        (ByteArrayTransformer, "ByteArray", ByteArray),
        (MemoryViewTransformer, "MemoryView", MemoryView),
        (ComplexTransformer, "Complex", Complex),
        (RangeTransformer, "Range", Range),
        (EnumerateTransformer, "Enumerate", Enumerate),
        (ZipTransformer, "Zip", Zip),
        (BlockTransformer, "Block", Block),
    ],
)
def test_public_type_binding_is_in_transformer(
    transformer: type[BaseTransformer], name: str, type_: type
) -> None:
    assert transformer.BINDINGS[name] is type_


@pytest.mark.parametrize(
    "name",
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
    ],
)
def test_public_type_binding_is_in_default_namespace(name: str) -> None:
    assert name in DEFAULT_NAMESPACE


@pytest.mark.parametrize(
    ("literal", "capitalized"),
    [
        ('"hi"', "Str"),
        ("(42)", "Int"),
        ("(3.14)", "Float"),
        ("True", "Boolean"),
        ("[1]", "List"),
        ("(1,)", "Tuple"),
        ("{1: 2}", "Dict"),
        ("{1, 2}", "Set"),
    ],
)
def test_is_instance_resolves_capitalized_name(literal: str, capitalized: str) -> None:
    assert bool(_eval(f"{literal}.is_instance({capitalized})")) is True


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
