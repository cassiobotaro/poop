import ast

from poop.validators.no_getattr import NoGetattrValidator


def test_method_named_getattr_is_not_rejected() -> None:
    tree = ast.parse("class Foo:\n    def m(self):\n        self.get_attr('x')")
    NoGetattrValidator().validate(tree)
