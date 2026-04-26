from poop.validators._call_name import make_call_name_validator

NoSliceValidator = make_call_name_validator(
    forbidden={"slice"},
    message="slice() is forbidden — use obj.copy_from_to(start, stop) or obj.copy_from_to(start, stop, step) instead",
)
