from poop.validators._call_name import make_call_name_validator

NoSetattrValidator = make_call_name_validator(
    forbidden={"setattr", "delattr"},
    message='{name}() is forbidden — use class methods to manage state instead',
)
