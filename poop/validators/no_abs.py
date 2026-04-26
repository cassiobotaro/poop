from poop.validators._call_name import make_call_name_validator

NoAbsValidator = make_call_name_validator(
    forbidden={'abs'},
    message='abs() is forbidden — use obj.abs() instead',
)
