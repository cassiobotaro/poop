from poop.validators._call_name import make_call_name_validator

NoGetattrValidator = make_call_name_validator(
    forbidden={"getattr"},
    message="getattr() is forbidden — use obj.get_attr(name) instead",
)
