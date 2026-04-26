from poop.validators._call_name import make_call_name_validator

NoHasattrValidator = make_call_name_validator(
    forbidden={'hasattr'},
    message='hasattr() is forbidden — use obj.has_attr(name) instead',
)
