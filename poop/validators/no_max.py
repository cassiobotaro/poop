from poop.validators._call_name import make_call_name_validator

NoMaxValidator = make_call_name_validator(
    forbidden={'max'},
    message='max() is forbidden — use a.max(b) instead',
)
