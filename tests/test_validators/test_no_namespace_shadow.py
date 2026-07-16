import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_namespace_shadow import NoNamespaceShadowValidator

# The protected set is whatever DEFAULT_NAMESPACE holds — today just Try
# and With. Both are language constructs rather than library surface, so
# unlike the mirror-era names they have no reason to disappear.


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2\ny = x.times(2)")
    NoNamespaceShadowValidator().validate(tree)


def test_assign_to_Try_raises() -> None:
    tree = ast.parse("Try = 42")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert "Try" in str(exc_info.value)
    assert "shadow" in str(exc_info.value).lower()


def test_assign_to_With_raises() -> None:
    tree = ast.parse("With = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_annotated_assignment_raises() -> None:
    tree = ast.parse("Try: int = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_augmented_assignment_raises() -> None:
    tree = ast.parse("Try += 1")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_tuple_unpacking_with_protected_name_raises() -> None:
    tree = ast.parse("Try, x = 1, 2")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert "Try" in str(exc_info.value)


def test_starred_unpacking_with_protected_name_raises() -> None:
    tree = ast.parse("a, *With = [1, 2, 3]")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_class_named_Try_raises() -> None:
    tree = ast.parse("class Try:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert "Try" in str(exc_info.value)


def test_assignment_inside_method_also_raises() -> None:
    # Even local shadowing is caught — the user would hit `Try(...)`
    # failing in confusing ways otherwise.
    tree = ast.parse("class Foo:\n    def m(self):\n        Try = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_method_parameter_with_protected_name_raises() -> None:
    # A parameter named after a binding shadows it inside the body exactly
    # like a local assignment does.
    tree = ast.parse("class Foo:\n    def m(self, Try):\n        return Try")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_keyword_only_parameter_with_protected_name_raises() -> None:
    tree = ast.parse("class Foo:\n    def m(self, *, With):\n        return With")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_vararg_with_protected_name_raises() -> None:
    tree = ast.parse("class Foo:\n    def m(self, *Try):\n        return Try")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_lambda_parameter_with_protected_name_raises() -> None:
    # proposal 153: lambdas (POOP's block form) carry most user code, so
    # the shadowing hazard applies to them too.
    tree = ast.parse("f = lambda Try: Try")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_lambda_vararg_with_protected_name_raises() -> None:
    tree = ast.parse("f = lambda *With: With")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_lambda_ordinary_parameter_passes() -> None:
    tree = ast.parse("f = lambda x: x")
    NoNamespaceShadowValidator().validate(tree)


def test_ordinary_parameters_pass() -> None:
    tree = ast.parse("class Foo:\n    def m(self, value, other):\n        return value")
    NoNamespaceShadowValidator().validate(tree)


def test_assigning_unrelated_name_passes() -> None:
    tree = ast.parse("Trying = 42\nm = 'something'")
    NoNamespaceShadowValidator().validate(tree)


def test_former_mirror_name_passes() -> None:
    # `math` was protected while the stdlib mirrors existed. It is an
    # ordinary name now — nothing to shadow.
    tree = ast.parse("math = 42")
    NoNamespaceShadowValidator().validate(tree)


def test_method_named_Try_is_fine() -> None:
    # Methods on a class don't bind `Try` at module scope.
    tree = ast.parse("class Calc:\n    def Try(self):\n        pass")
    NoNamespaceShadowValidator().validate(tree)


def test_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\nTry = 2")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert exc_info.value.lineno == 2


def test_nested_def_named_Try_raises() -> None:
    # A def nested in a method binds a real local name, so a later `Try(...)`
    # in that body resolves to it instead of the runtime entry point. The
    # assignment form is rejected; this one must be too.
    source = (
        "class Demo:\n    def run(self):\n        def Try(block):\n            return 1"
    )
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="'Try'"):
        NoNamespaceShadowValidator().validate(tree)


def test_nested_async_def_named_Try_raises() -> None:
    source = "class Demo:\n    def run(self):\n        async def Try(block):\n            return 1"
    tree = ast.parse(source)
    with pytest.raises(ValidationError, match="'Try'"):
        NoNamespaceShadowValidator().validate(tree)


def test_nested_def_named_Try_carries_line_number() -> None:
    source = (
        "class Demo:\n    def run(self):\n        def Try(block):\n            return 1"
    )
    tree = ast.parse(source)
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert exc_info.value.lineno == 3


def test_method_named_Try_in_nested_class_is_fine() -> None:
    # The class-body carve-out still applies one level down.
    source = "class Outer:\n    class Inner:\n        def Try(self):\n            pass"
    tree = ast.parse(source)
    NoNamespaceShadowValidator().validate(tree)
