import ast

from poop.validators.no_isinstance import NoIsinstanceValidator


def test_method_named_isinstance_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.is_kind_of(int)")
    NoIsinstanceValidator().validate(tree)
