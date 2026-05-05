from poop.validators._call_name import make_call_name_validator

NoEnumerateValidator = make_call_name_validator(
    forbidden={"enumerate", "zip"},
    message="{name}() is forbidden — use collection messages map(block), do(block) instead",
)
