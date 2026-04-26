from poop.validators._call_name import make_call_name_validator

NoSortedValidator = make_call_name_validator(
    forbidden={'sorted'},
    message='sorted() is forbidden — use col.sorted() instead',
)
