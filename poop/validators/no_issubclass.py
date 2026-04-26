from poop.validators._call_name import make_call_name_validator

NoIssubclassValidator = make_call_name_validator(
    forbidden={'issubclass'},
    message='issubclass() is forbidden — use Class.is_subclass(Other) instead',
)
