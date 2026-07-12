import ast

from poop.validators._node import make_node_validator

NoFstringValidator = make_node_validator(
    {
        ast.JoinedStr: (
            "f-strings are forbidden — build strings with concatenation, "
            'e.g. ("Hello, " + name) or ("count: " + str(n))'
        ),
        ast.TemplateStr: (
            "t-strings are forbidden — the same {...} interpolation hides "
            "message sends and yields a raw Template, bypassing POOP Str; "
            'build strings with concatenation, e.g. ("count: " + str(n))'
        ),
    }
)
