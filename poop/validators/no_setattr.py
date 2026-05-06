from poop.validators._call_name import make_call_name_validator

NoSetattrValidator = make_call_name_validator(
    forbidden={"setattr", "delattr"},
    message="{name}() is forbidden — use obj.set_attr(name, val) / obj.del_attr(name) instead",
)
