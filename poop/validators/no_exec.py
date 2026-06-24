from poop.validators._call_name import make_call_name_validator

NoExecValidator = make_call_name_validator(
    forbidden={"exec", "eval", "compile", "__import__"},
    message="{name}() is forbidden — metaprogramming is not allowed",
)
