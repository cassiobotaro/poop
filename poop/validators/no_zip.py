from poop.validators._call_name import make_call_name_validator

NoZipValidator = make_call_name_validator(
    forbidden={"zip"},
    message="{name}() is forbidden — use collection messages map(block), do(block) instead",
)
