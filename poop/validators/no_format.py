"""`format(x, spec)` is a free function; `x.format(spec)` is the message.

The substitute has one exception and the ban has to name it. `Str.format` is
POOP's *template* surface — the `"{}".format(x)` method f-strings were banned in
favour of — so a spec handed to it is read as an argument for placeholders the
string does not have, and `str.format` discards extra positional arguments:

    (5).format(">6")     # '     5'
    (2.5).format(".2f")  # '2.50'
    "ab".format(">6")    # 'ab'      — unchanged, silently

A reader who followed the old wording got their string back, three times out of
three, with no way to tell it had not worked. CPython refuses two of those three
outright, so even the faithful behaviour would have been louder.

The two meanings cannot both live on one selector without deciding by
inspection — "a value whose class and contents disagree", which proposal 9
refused elsewhere — so the template keeps `Str.format` and the ban points a
`Str` at the spelling that actually works.
"""

from poop.validators._call_name import make_call_name_validator

NoFormatValidator = make_call_name_validator(
    forbidden={"format"},
    message=(
        "format() is forbidden — use obj.format(spec) instead, "
        'or "{{:spec}}".format(text) for a str, whose #format is the template'
    ),
)
