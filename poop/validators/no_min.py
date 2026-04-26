from poop.validators._call_name import make_call_name_validator

NoMinValidator = make_call_name_validator(
    forbidden={'min'},
    message='min() is forbidden — use a.min(b) instead',
)
