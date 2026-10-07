"""The contract every `CallNameValidator` shares, stated once.

A call-name validator is two class attributes — `forbidden` and `message` —
over one visitor, so its mechanical behaviour is the base's: any `Name` node
spelling a forbidden builtin is refused, wherever it stands; an attribute or a
keyword of the same spelling is not a `Name` and passes. Each validator's own
test module keeps only what is specific to it.
"""

import ast
import re
from typing import TYPE_CHECKING

import pytest

from poop.errors import ValidationError
from poop.validators import DEFAULT_VALIDATORS
from poop.validators._call_name import CallNameValidator

if TYPE_CHECKING:
    from poop.validators.base import Validator

CALL_NAMES = [
    pytest.param(validator, name, id=name)
    for validator in DEFAULT_VALIDATORS
    if isinstance(validator, CallNameValidator)
    for name in sorted(validator.forbidden)
]

# A bare reference to a forbidden builtin in any position — not only a call —
# reopens the wrapper layer: `f = len` and `xs.map(len)` would hand user code
# the raw builtin, so the names are reserved outright.
REFUSED = {
    "call": "{name}(x)",
    "call without arguments": "{name}()",
    "call inside a method": "class Foo:\n    def m(self):\n        {name}(self)",
    "passed as a value": "f = {name}",
    "passed as an argument": "xs.map({name})",
    "assignment target": "{name} = 5",
}

ALLOWED = {
    "method on self": "class Foo:\n    def m(self):\n        self.{name}()",
    "method on an object": "obj.{name}()",
    "keyword argument": "obj.call({name}=1)",
}


def _validator_id(validator: Validator) -> str:
    return type(validator).__name__


@pytest.mark.parametrize("validator", DEFAULT_VALIDATORS, ids=_validator_id)
def test_plain_code_passes(validator: Validator) -> None:
    validator.validate(ast.parse("x = 1 + 2\ny = x.times(2)\nz = [1, 2, 3]"))


@pytest.mark.parametrize("shape", REFUSED)
@pytest.mark.parametrize(("validator", "name"), CALL_NAMES)
def test_forbidden_name_is_refused(
    validator: CallNameValidator, name: str, shape: str
) -> None:
    expected = validator.message.format(name=name)
    tree = ast.parse(REFUSED[shape].format(name=name))
    with pytest.raises(ValidationError, match=re.escape(expected)) as exc_info:
        validator.validate(tree)
    assert exc_info.value.message == expected


@pytest.mark.parametrize(("validator", "name"), CALL_NAMES)
def test_refusal_carries_line_number(validator: CallNameValidator, name: str) -> None:
    tree = ast.parse(f"x = 1\ny = {name}(x)")
    with pytest.raises(ValidationError) as exc_info:
        validator.validate(tree)
    assert exc_info.value.lineno == 2
    assert exc_info.value.col_offset == 4


@pytest.mark.parametrize("shape", ALLOWED)
@pytest.mark.parametrize(("validator", "name"), CALL_NAMES)
def test_same_spelling_off_a_name_passes(
    validator: CallNameValidator, name: str, shape: str
) -> None:
    validator.validate(ast.parse(ALLOWED[shape].format(name=name)))
