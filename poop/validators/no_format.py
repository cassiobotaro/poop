"""`format(x, spec)` is a free function; `x.format(spec)` is the message.

The substitute has one exception and the ban has to name it. `Str.format` is
POOP's *template* surface — the `"{}".format(x)` method f-strings were banned in
favour of — so a spec handed to it is read as an argument for placeholders the
string does not have, and `str.format` discards extra positional arguments:

    (5).format(">6")     # '     5'
    (2.5).format(".2f")  # '2.50'
    "ab".format(">6")    # 'ab'      — unchanged, silently

A message naming only `obj.format(spec)` would hand a `str` reader their string
back unchanged, with no way to tell it had not worked.

The two meanings cannot both live on one selector without deciding by
inspection — "a value whose class and contents disagree", which POOP refuses
elsewhere — so the template keeps `Str.format` and the ban points a
`Str` at the spelling that actually works
(`doc/adr/0022-str-format-is-the-only-template-surface.md`).
"""

from poop.validators._call_name import CallNameValidator


class NoFormatValidator(CallNameValidator):
    forbidden = frozenset({"format"})
    message = (
        "format() is forbidden — use obj.format(spec) instead, "
        'or "{{:spec}}".format(text) for a str, whose #format is the template'
    )
