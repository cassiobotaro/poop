from poop.validators._call_name import make_call_name_validator

NoReversedValidator = make_call_name_validator(
    forbidden={'reversed'},
    message='reversed() is forbidden — use col.reversed() instead',
)
