from poop.validators._call_name import make_call_name_validator

NoIsinstanceValidator = make_call_name_validator(
    forbidden={"isinstance"},
    message="isinstance() is forbidden — use obj.is_instance(Type) instead",
)
