from poop.validators._call_name import make_call_name_validator

NoLenValidator = make_call_name_validator(
    forbidden={'len'},
    message='len() is forbidden — use obj.len() instead',
)
