import ast

from poop.validators.no_issubclass import NoIssubclassValidator


def test_method_named_issubclass_is_not_rejected() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.is_subclass(Other)")
    NoIssubclassValidator().validate(tree)
