from poop.validators._call_name import make_call_name_validator

NoSliceValidator = make_call_name_validator(
    forbidden={"slice"},
    message="slice() is forbidden — use Slice(start, stop) or Slice(start, stop, step) to construct a reusable slice value, or obj.slice(start, stop) / obj.slice(start, stop, step) as a method call instead",
)
