import ast

from poop.validators._node import make_node_validator

NoFstringValidator = make_node_validator(
    {
        ast.JoinedStr: (
            "f-strings are forbidden — build strings with concatenation, "
            'e.g. ("Hello, " + name) or ("count: " + str(n))'
        ),
    }
)
