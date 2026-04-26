from poop.validators._call_name import make_call_name_validator

NoCallableValidator = make_call_name_validator(
    forbidden={'callable'},
    message='callable() is forbidden — use obj.callable() instead',
)
