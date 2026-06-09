from poop.validators._call_name import make_call_name_validator

NoTypeValidator = make_call_name_validator(
    forbidden={"type"},
    message="type() is forbidden — use obj.class_name() or polymorphism instead",
)
