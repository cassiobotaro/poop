from poop.validators._call_name import make_call_name_validator

NoIterValidator = make_call_name_validator(
    forbidden={"iter", "next", "aiter", "anext"},
    message="{name}() is forbidden — use col.iter() / it.next() instead",
)
