from poop.validators._call_name import CallNameValidator


class NoSetattrValidator(CallNameValidator):
    forbidden = frozenset({"setattr", "delattr"})
    message = "{name}() is forbidden — use obj.set_attr(name, val) / obj.del_attr(name) instead"
