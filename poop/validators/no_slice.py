from poop.validators._call_name import make_call_name_validator

NoSliceValidator = make_call_name_validator(
    forbidden={"slice"},
    message="slice() is forbidden — use obj.slice(start, stop) or obj.slice(start, stop, step) instead",
)
