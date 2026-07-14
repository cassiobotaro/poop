import ast

import pytest

from poop.errors import ValidationError
from poop.validators.no_namespace_shadow import NoNamespaceShadowValidator


def test_valid_code_passes() -> None:
    tree = ast.parse("x = 1 + 2\ny = x.times(2)")
    NoNamespaceShadowValidator().validate(tree)


def test_assign_to_io_raises() -> None:
    tree = ast.parse("io = 42")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert "io" in str(exc_info.value)
    assert "shadow" in str(exc_info.value).lower()


def test_assign_to_Path_raises() -> None:
    tree = ast.parse("Path = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_assign_to_StringIO_class_raises() -> None:
    # `io` binds both the lowercase module entry point and the classes it
    # exposes; shadowing either one breaks the same namespace.
    tree = ast.parse("StringIO = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_assign_to_Try_raises() -> None:
    tree = ast.parse("Try = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_assign_to_With_raises() -> None:
    tree = ast.parse("With = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_assign_to_AsyncWith_raises() -> None:
    tree = ast.parse("AsyncWith = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_annotated_assignment_raises() -> None:
    tree = ast.parse("io: int = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_augmented_assignment_raises() -> None:
    tree = ast.parse("io += 1")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_tuple_unpacking_with_protected_name_raises() -> None:
    tree = ast.parse("io, x = 1, 2")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert "io" in str(exc_info.value)


def test_starred_unpacking_with_protected_name_raises() -> None:
    tree = ast.parse("a, *io = [1, 2, 3]")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_class_named_io_raises() -> None:
    tree = ast.parse("class io:\n    pass")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert "io" in str(exc_info.value)


def test_assignment_inside_method_also_raises() -> None:
    # Even local shadowing is caught — the user would hit
    # `io.StringIO(...)` failing in confusing ways otherwise.
    tree = ast.parse("class Foo:\n    def m(self):\n        io = 42")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_method_parameter_with_protected_name_raises() -> None:
    # A parameter named after a binding shadows it inside the body exactly
    # like a local assignment does (io.StringIO would fail confusingly).
    tree = ast.parse("class Foo:\n    def m(self, io):\n        return io")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_async_method_parameter_with_protected_name_raises() -> None:
    tree = ast.parse("class Foo:\n    async def m(self, Path):\n        return Path")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_keyword_only_parameter_with_protected_name_raises() -> None:
    tree = ast.parse("class Foo:\n    def m(self, *, BytesIO):\n        return BytesIO")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_vararg_with_protected_name_raises() -> None:
    tree = ast.parse("class Foo:\n    def m(self, *io):\n        return io")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_lambda_parameter_with_protected_name_raises() -> None:
    # proposal 153: lambdas (POOP's block form) carry most user code, so
    # the shadowing hazard applies to them too.
    tree = ast.parse("f = lambda io: io")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_lambda_vararg_with_protected_name_raises() -> None:
    tree = ast.parse("f = lambda *Path: Path")
    with pytest.raises(ValidationError, match="POOP namespace"):
        NoNamespaceShadowValidator().validate(tree)


def test_lambda_ordinary_parameter_passes() -> None:
    tree = ast.parse("f = lambda x: x")
    NoNamespaceShadowValidator().validate(tree)


def test_ordinary_parameters_pass() -> None:
    tree = ast.parse("class Foo:\n    def m(self, value, other):\n        return value")
    NoNamespaceShadowValidator().validate(tree)


def test_assigning_unrelated_name_passes() -> None:
    tree = ast.parse("iodine = 42\nm = 'something'")
    NoNamespaceShadowValidator().validate(tree)


def test_unprotected_lowercase_passes() -> None:
    # Names that look similar but are not bound do not trigger.
    tree = ast.parse("wave = 42")
    NoNamespaceShadowValidator().validate(tree)


def test_method_named_io_is_fine() -> None:
    # Methods on a class don't bind `io` at module scope.
    tree = ast.parse("class Calc:\n    def io(self):\n        pass")
    NoNamespaceShadowValidator().validate(tree)


def test_error_carries_line_number() -> None:
    tree = ast.parse("x = 1\nio = 2")
    with pytest.raises(ValidationError) as exc_info:
        NoNamespaceShadowValidator().validate(tree)
    assert exc_info.value.lineno == 2
