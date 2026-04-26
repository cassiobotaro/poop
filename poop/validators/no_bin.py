from poop.validators._call_name import make_call_name_validator

NoBinValidator = make_call_name_validator(
    forbidden={"bin", "hex", "oct"},
    message='{name}() is forbidden — use n.{name}() instead',
)
