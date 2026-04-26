from poop.validators._call_name import make_call_name_validator

NoChrValidator = make_call_name_validator(
    forbidden={"chr", "ord"},
    message='{name}() is forbidden — use obj.{name}() instead',
)
