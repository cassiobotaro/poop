from poop.validators._call_name import make_call_name_validator

NoHelpValidator = make_call_name_validator(
    forbidden={"help"},
    message="help() is forbidden — no POOP equivalent",
)
