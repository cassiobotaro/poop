from poop.validators._call_name import make_call_name_validator

NoExitValidator = make_call_name_validator(
    forbidden={"exit", "quit"},
    message='{name}() is forbidden — no POOP equivalent',
)
