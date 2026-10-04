from poop.validators._call_name import CallNameValidator


class NoHelpValidator(CallNameValidator):
    forbidden = frozenset({"help"})
    message = "help() is forbidden — no POOP equivalent"
