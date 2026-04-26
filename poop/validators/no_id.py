from poop.validators._call_name import make_call_name_validator

NoIdValidator = make_call_name_validator(
    forbidden={'id'},
    message='id() is forbidden — use obj.id() instead',
)
