import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.email import Email, EmailMessage, EmailPolicy, EmailUtils
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import none
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_emailmessage_constructs() -> None:
    m = EmailMessage()
    assert isinstance(m, EmailMessage)


def test_emailmessage_set_get_content() -> None:
    m = EmailMessage()
    m.set_content(Str("hello"))
    body = m.get_content()
    assert isinstance(body, Str)
    assert "hello" in body._value


def test_emailmessage_set_content_with_subtype() -> None:
    m = EmailMessage()
    m.set_content(Str("<p>hi</p>"), Str("html"))
    assert isinstance(m.get_content(), Str)


def test_emailmessage_headers_round_trip() -> None:
    m = EmailMessage()
    m.at_put(Str("From"), Str("a@example.com"))
    m.at_put(Str("To"), Str("b@example.com"))
    m.at_put(Str("Subject"), Str("hi"))
    assert m.at(Str("Subject")) == Str("hi")


def test_emailmessage_missing_header_returns_none() -> None:
    m = EmailMessage()
    assert m.at(Str("X-Missing")) is none


def test_emailmessage_keys_values_items() -> None:
    m = EmailMessage()
    m.at_put(Str("From"), Str("a@example.com"))
    assert isinstance(m.keys(), List)
    assert isinstance(m.values(), List)
    assert isinstance(m.items(), List)


def test_emailmessage_is_multipart_initially_false() -> None:
    m = EmailMessage()
    m.set_content(Str("hi"))
    assert m.is_multipart() is false


def test_emailmessage_as_string_is_str() -> None:
    m = EmailMessage()
    m.set_content(Str("body"))
    assert isinstance(m.as_string(), Str)


def test_emailmessage_as_bytes_is_bytes() -> None:
    m = EmailMessage()
    m.set_content(Str("body"))
    assert isinstance(m.as_bytes(), Bytes)


def test_emailmessage_add_alternative_makes_multipart() -> None:
    m = EmailMessage()
    m.set_content(Str("plain"))
    m.add_alternative(Str("<p>html</p>"), Str("html"))
    assert m.is_multipart() is true


def test_emailmessage_add_attachment() -> None:
    m = EmailMessage()
    m.set_content(Str("body"))
    m.add_attachment(Bytes(b"DATA"), Str("application"), Str("octet-stream"))
    assert m.is_multipart() is true


def test_emailmessage_add_attachment_with_filename() -> None:
    m = EmailMessage()
    m.set_content(Str("body"))
    m.add_attachment(
        Bytes(b"DATA"), Str("application"), Str("octet-stream"), Str("payload.bin")
    )
    assert m.is_multipart() is true


def test_emailmessage_iter_parts_multipart() -> None:
    m = EmailMessage()
    m.set_content(Str("plain"))
    m.add_alternative(Str("<p>html</p>"), Str("html"))
    parts = m.iter_parts()
    assert isinstance(parts, List)


def test_emailmessage_iter_attachments() -> None:
    m = EmailMessage()
    m.set_content(Str("body"))
    m.add_attachment(Bytes(b"X"), Str("text"), Str("plain"))
    atts = m.iter_attachments()
    assert isinstance(atts, List)


def test_emailmessage_get_body_default() -> None:
    m = EmailMessage()
    m.set_content(Str("body"))
    assert isinstance(m.get_body(), EmailMessage)


def test_emailmessage_get_body_with_preferencelist() -> None:
    m = EmailMessage()
    m.set_content(Str("plain"))
    m.add_alternative(Str("<p>html</p>"), Str("html"))
    body = m.get_body(List(Str("html"), Str("plain")))
    assert isinstance(body, EmailMessage)


def test_emailmessage_get_body_preferencelist_type_check() -> None:
    m = EmailMessage()
    m.set_content(Str("body"))
    with pytest.raises(TypeError):
        m.get_body(List(Int(1)))


def test_emailmessage_repr_returns_python_str() -> None:
    m = EmailMessage()
    m.set_content(Str("hi"))
    text = repr(m)
    assert isinstance(text, str)
    assert "hi" in text


# --- email.message_from_string / message_from_bytes ---


def test_email_message_from_string() -> None:
    raw = "Subject: hi\r\nFrom: a@b.c\r\n\r\nbody\r\n"
    m = Email.message_from_string(Str(raw))
    assert isinstance(m, EmailMessage)
    assert m.at(Str("Subject")) == Str("hi")


def test_email_message_from_bytes() -> None:
    raw = b"Subject: hi\r\nFrom: a@b.c\r\n\r\nbody\r\n"
    m = Email.message_from_bytes(Bytes(raw))
    assert isinstance(m, EmailMessage)
    assert m.at(Str("Subject")) == Str("hi")


# --- email.utils ---


def test_utils_parseaddr() -> None:
    result = EmailUtils.parseaddr(Str("Foo Bar <foo@bar.com>"))
    assert isinstance(result, Tuple)
    assert result.at(Int(0)) == Str("Foo Bar")
    assert result.at(Int(1)) == Str("foo@bar.com")


def test_utils_formataddr() -> None:
    s = EmailUtils.formataddr(Tuple(Str("Foo Bar"), Str("foo@bar.com")))
    assert isinstance(s, Str)
    assert "foo@bar.com" in s._value


def test_utils_formataddr_bad_arity() -> None:
    with pytest.raises(ValueError):
        EmailUtils.formataddr(Tuple(Str("only")))


def test_utils_formataddr_type_check() -> None:
    with pytest.raises(TypeError):
        EmailUtils.formataddr(Tuple(Int(1), Int(2)))


def test_utils_getaddresses() -> None:
    addrs = EmailUtils.getaddresses(List(Str("a@x.com, b@x.com")))
    assert isinstance(addrs, List)
    assert addrs.len() == Int(2)


def test_utils_getaddresses_type_check() -> None:
    with pytest.raises(TypeError):
        EmailUtils.getaddresses(List(Int(1)))


def test_utils_parsedate() -> None:
    result = EmailUtils.parsedate(Str("Mon, 16 May 2026 12:00:00 -0000"))
    assert isinstance(result, Tuple)


def test_utils_parsedate_invalid_returns_none() -> None:
    assert EmailUtils.parsedate(Str("not a date")) is none


def test_utils_formatdate_no_args() -> None:
    assert isinstance(EmailUtils.formatdate(), Str)


def test_utils_formatdate_with_args() -> None:
    s = EmailUtils.formatdate(Int(0), false, true)
    assert "GMT" in s._value


def test_utils_make_msgid_no_args() -> None:
    msgid = EmailUtils.make_msgid()
    assert msgid._value.startswith("<")


def test_utils_make_msgid_with_idstring_and_domain() -> None:
    msgid = EmailUtils.make_msgid(Str("xy"), Str("example.com"))
    assert "example.com" in msgid._value


# --- email.policy ---


def test_policy_default_exists() -> None:
    assert EmailPolicy.default is not None
    assert EmailPolicy.SMTP is not None
    assert EmailPolicy.SMTPUTF8 is not None
    assert EmailPolicy.HTTP is not None
    assert EmailPolicy.strict is not None
    assert EmailPolicy.compat32 is not None


def test_email_class_refs() -> None:
    assert Email.EmailMessage is EmailMessage
    assert Email.utils is EmailUtils
    assert Email.policy is EmailPolicy


# --- Interpreter integration ---


def test_email_construct_via_interpreter() -> None:
    Interpreter().run_source(
        'm = EmailMessage()\nm.set_content("hi")\nm.as_string().print()'
    )
