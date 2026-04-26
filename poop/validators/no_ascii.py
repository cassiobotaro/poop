from poop.validators._call_name import make_call_name_validator

NoAsciiValidator = make_call_name_validator(
    forbidden={'ascii'},
    message='ascii() is forbidden — use obj.ascii() instead',
)
