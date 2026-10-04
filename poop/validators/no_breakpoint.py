from poop.validators._call_name import CallNameValidator


class NoBreakpointValidator(CallNameValidator):
    forbidden = frozenset({"breakpoint"})
    message = "breakpoint() is forbidden — no POOP equivalent"
