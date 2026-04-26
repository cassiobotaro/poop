from poop.validators._call_name import make_call_name_validator

NoDirValidator = make_call_name_validator(
    forbidden={"dir"},
    message="dir() is forbidden — use obj.dir() instead",
)
