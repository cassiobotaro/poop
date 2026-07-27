from poop.validators._call_name import make_call_name_validator

# `obj.id()` used to be the substitute named here, and it answered CPython's
# address: a number describing the process rather than the program, recycled
# under a live object, and identical to `obj.hash()` for anything that does not
# hash by value. `is_identical` answers the comparison `id()` exists to enable
# without materialising a number at all; keying a Dict by identity is the only
# thing it does not cover, and nothing in POOP asks for that.
NoIdValidator = make_call_name_validator(
    forbidden={"id"},
    message="id() is forbidden — use a.is_identical(b) to compare identity",
)
