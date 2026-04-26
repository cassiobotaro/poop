from poop.validators._call_name import make_call_name_validator

NoMapValidator = make_call_name_validator(
    forbidden={"map"},
    message="map() is forbidden — use col.map(block) instead",
)
