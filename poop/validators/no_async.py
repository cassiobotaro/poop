import ast

from poop.validators._node import make_node_validator

NoAsyncValidator = make_node_validator(
    {
        ast.AsyncFunctionDef: "async functions are forbidden — POOP has no event loop",
        ast.Await: "await is forbidden — POOP has no event loop",
    }
)
