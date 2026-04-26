from poop.validators._call_name import make_call_name_validator

NoPrintValidator = make_call_name_validator(
    forbidden={'print'},
    message='print is forbidden — use obj.print() instead',
)
