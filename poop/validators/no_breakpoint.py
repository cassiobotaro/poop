from poop.validators._call_name import make_call_name_validator

NoBreakpointValidator = make_call_name_validator(
    forbidden={"breakpoint"},
    message="breakpoint() is forbidden — no POOP equivalent",
)
