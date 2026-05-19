from poop.interpreter import Interpreter
from poop.types.boolean import true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.smtplib import LMTP, SMTP, SMTP_SSL, Smtplib
from poop.types.string import Str

# --- Constants ---


def test_smtp_constants() -> None:
    assert Smtplib.SMTP_PORT == Int(25)
    assert Smtplib.SMTP_SSL_PORT == Int(465)
    assert Smtplib.LMTP_PORT == Int(2003)


def test_crlf_constants() -> None:
    assert Smtplib.CRLF == Str("\r\n")
    assert Smtplib.bCRLF == Bytes(b"\r\n")


# --- Error hierarchy ---


def test_smtp_exception_hierarchy() -> None:
    assert issubclass(Smtplib.SMTPException, Exception)
    assert issubclass(Smtplib.SMTPServerDisconnected, Smtplib.SMTPException)
    assert issubclass(Smtplib.SMTPResponseException, Smtplib.SMTPException)
    assert issubclass(Smtplib.SMTPSenderRefused, Smtplib.SMTPResponseException)
    assert issubclass(Smtplib.SMTPRecipientsRefused, Smtplib.SMTPException)
    assert issubclass(Smtplib.SMTPDataError, Smtplib.SMTPResponseException)
    assert issubclass(Smtplib.SMTPConnectError, Smtplib.SMTPResponseException)
    assert issubclass(Smtplib.SMTPHeloError, Smtplib.SMTPResponseException)
    assert issubclass(Smtplib.SMTPNotSupportedError, Smtplib.SMTPException)
    assert issubclass(Smtplib.SMTPAuthenticationError, Smtplib.SMTPResponseException)


# --- Construction (no network round-trip) ---


def test_smtp_construction_without_connect() -> None:
    # No host argument means the wrapper doesn't try to connect.
    smtp = SMTP()
    assert isinstance(smtp, SMTP)
    smtp.close()


def test_smtp_ssl_construction_without_connect() -> None:
    smtp = SMTP_SSL()
    assert isinstance(smtp, SMTP_SSL)
    smtp.close()


def test_lmtp_construction_without_connect() -> None:
    lmtp = LMTP()
    assert isinstance(lmtp, LMTP)
    lmtp.close()


def test_set_debuglevel_returns_none() -> None:
    smtp = SMTP()
    try:
        result = smtp.set_debuglevel(Int(0))
        from poop.types.none import none

        assert result is none
    finally:
        smtp.close()


# --- Class refs ---


def test_smtplib_class_refs() -> None:
    assert Smtplib.SMTP is SMTP
    assert Smtplib.SMTP_SSL is SMTP_SSL
    assert Smtplib.LMTP is LMTP


# --- Method surface check (via attribute presence) ---


def test_smtp_method_surface() -> None:
    smtp = SMTP()
    try:
        for name in (
            "connect",
            "helo",
            "ehlo",
            "has_extn",
            "starttls",
            "login",
            "sendmail",
            "send_message",
            "quit",
            "set_debuglevel",
            "docmd",
            "noop",
            "verify",
            "expn",
            "rset",
            "close",
        ):
            assert callable(getattr(smtp, name))
    finally:
        smtp.close()


# --- Interpreter integration ---


def test_smtp_constants_via_interpreter() -> None:
    Interpreter().run_source("smtplib.SMTP_PORT.print()")


def test_smtp_class_reachable_via_interpreter() -> None:
    Interpreter().run_source("smtp = SMTP()\nsmtp.close()")


# --- Method delegation via a mock _impl ---


class _MockSMTPImpl:
    """A test-only stand-in for `smtplib.SMTP`'s impl — records calls
    and returns canned `(code, b"msg")` tuples so the wrapper's
    POOP↔Python conversion can be exercised without a network round
    trip."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def _record(self, name: str, *args, **kwargs) -> tuple[int, bytes]:
        self.calls.append((name, args, kwargs))
        return (250, b"OK")

    def connect(self, **kwargs) -> tuple[int, bytes]:
        return self._record("connect", **kwargs)

    def helo(self, name: str = "") -> tuple[int, bytes]:
        return self._record("helo", name)

    def ehlo(self, name: str = "") -> tuple[int, bytes]:
        return self._record("ehlo", name)

    def has_extn(self, name: str) -> bool:
        self.calls.append(("has_extn", (name,), {}))
        return True

    def docmd(self, cmd: str, args: str = "") -> tuple[int, bytes]:
        return self._record("docmd", cmd, args)

    def noop(self) -> tuple[int, bytes]:
        return self._record("noop")

    def verify(self, address: str) -> tuple[int, bytes]:
        return self._record("verify", address)

    def expn(self, address: str) -> tuple[int, bytes]:
        return self._record("expn", address)

    def rset(self) -> tuple[int, bytes]:
        return self._record("rset")

    def starttls(self) -> tuple[int, bytes]:
        return self._record("starttls")

    def login(self, user: str, password: str) -> tuple[int, bytes]:
        return self._record("login", user, password)

    def sendmail(self, *args, **kwargs):
        self.calls.append(("sendmail", args, kwargs))
        return {"failed@example.com": (550, b"refused")}

    def send_message(self, *args, **kwargs):
        self.calls.append(("send_message", args, kwargs))
        return {}

    def quit(self) -> tuple[int, bytes]:
        return self._record("quit")

    def close(self) -> None:
        self.calls.append(("close", (), {}))

    def set_debuglevel(self, level: int) -> None:
        self.calls.append(("set_debuglevel", (level,), {}))


def _make_mock_smtp() -> tuple[SMTP, _MockSMTPImpl]:
    smtp = SMTP()
    smtp.close()  # close the real impl
    mock = _MockSMTPImpl()
    smtp._impl = mock
    return smtp, mock


def test_helo_unwraps_and_wraps() -> None:
    from poop.types.tuple import Tuple

    smtp, mock = _make_mock_smtp()
    result = smtp.helo(Str("localhost"))
    assert mock.calls[0] == ("helo", ("localhost",), {})
    assert result == Tuple(Int(250), Bytes(b"OK"))


def test_ehlo_unwraps_and_wraps() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.ehlo(Str("client"))
    assert mock.calls[0] == ("ehlo", ("client",), {})


def test_has_extn_returns_bool() -> None:
    smtp, mock = _make_mock_smtp()
    assert smtp.has_extn(Str("STARTTLS")) is true
    assert mock.calls[0] == ("has_extn", ("STARTTLS",), {})


def test_docmd_and_noop_and_rset() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.docmd(Str("HELP"))
    smtp.noop()
    smtp.rset()
    names = [c[0] for c in mock.calls]
    assert names == ["docmd", "noop", "rset"]


def test_verify_and_expn() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.verify(Str("a@example.com"))
    smtp.expn(Str("staff@example.com"))
    assert mock.calls[0][1] == ("a@example.com",)
    assert mock.calls[1][1] == ("staff@example.com",)


def test_starttls_and_login() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.starttls()
    smtp.login(Str("user"), Str("password"))
    assert mock.calls[0][0] == "starttls"
    assert mock.calls[1] == ("login", ("user", "password"), {})


def test_connect_unwraps_host_and_port() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.connect(Str("smtp.example.com"), Int(587))
    assert mock.calls[0][2] == {"host": "smtp.example.com", "port": 587}


def test_sendmail_unwraps_list_recipients() -> None:
    from poop.types.list import List

    smtp, mock = _make_mock_smtp()
    result = smtp.sendmail(
        Str("from@example.com"),
        List(Str("a@example.com"), Str("b@example.com")),
        Str("Subject: hi\n\nBody"),
    )
    args = mock.calls[0][1]
    assert args[0] == "from@example.com"
    assert args[1] == ["a@example.com", "b@example.com"]
    assert args[2] == "Subject: hi\n\nBody"
    # Returned Dict maps recipient → Tuple(code, bytes).
    from poop.types.dict import Dict

    assert isinstance(result, Dict)


def test_sendmail_unwraps_str_recipient() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.sendmail(Str("from@example.com"), Str("rcpt@example.com"), Bytes(b"data"))
    args = mock.calls[0][1]
    assert args[1] == "rcpt@example.com"


def test_sendmail_with_options() -> None:
    from poop.types.list import List

    smtp, mock = _make_mock_smtp()
    smtp.sendmail(
        Str("a"),
        Str("b"),
        Bytes(b"data"),
        mail_options=List(Str("SIZE=1000")),
        rcpt_options=List(Str("NOTIFY=NEVER")),
    )
    kwargs = mock.calls[0][2]
    assert kwargs["mail_options"] == ["SIZE=1000"]
    assert kwargs["rcpt_options"] == ["NOTIFY=NEVER"]


def test_send_message_with_kwargs() -> None:
    from poop.types.list import List

    smtp, mock = _make_mock_smtp()
    smtp.send_message(
        object(),
        from_addr=Str("a@x"),
        to_addrs=List(Str("b@x")),
    )
    kwargs = mock.calls[0][2]
    assert kwargs["from_addr"] == "a@x"
    assert kwargs["to_addrs"] == ["b@x"]


def test_send_message_to_addrs_as_str() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.send_message(object(), to_addrs=Str("rcpt@x"))
    assert mock.calls[0][2]["to_addrs"] == "rcpt@x"


def test_quit_returns_tuple() -> None:
    smtp, mock = _make_mock_smtp()
    smtp.quit()
    assert mock.calls[0][0] == "quit"


def test_smtp_with_source_address() -> None:
    from poop.types.tuple import Tuple as PoopTuple

    smtp = SMTP(source_address=PoopTuple(Str("127.0.0.1"), Int(0)))
    smtp.close()
    assert isinstance(smtp, SMTP)


def test_smtp_ssl_with_args() -> None:
    smtp = SMTP_SSL(local_hostname=Str("client"), timeout=Int(30))
    smtp.close()
    assert isinstance(smtp, SMTP_SSL)


def test_lmtp_with_args() -> None:
    lmtp = LMTP(local_hostname=Str("client"))
    lmtp.close()
    assert isinstance(lmtp, LMTP)


# --- Context manager round trip ---


def test_smtp_context_manager() -> None:
    smtp, mock = _make_mock_smtp()
    # Provide a minimal __exit__ so the context-manager path runs.
    mock.__exit__ = lambda *args: None  # type: ignore[attr-defined]  # ty: ignore[unresolved-attribute]
    with smtp:
        pass
