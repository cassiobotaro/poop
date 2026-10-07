import ast

from poop.validators.no_hasattr import NoHasattrValidator


def test_method_named_has_attr_is_not_blocked() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.has_attr('foo')")
    NoHasattrValidator().validate(tree)
