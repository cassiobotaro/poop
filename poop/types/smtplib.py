from __future__ import annotations

import smtplib as _smtplib
from types import TracebackType
from typing import Any, ClassVar, Self

from poop.types.bytes import Bytes
from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _opt_str(value: Str | None, default: str) -> str:
    return default if value is None else value._value


def _wrap_helo_tuple(pair: tuple[int, bytes]) -> Tuple:
    code, msg = pair
    return Tuple(Int(code), Bytes(msg))


def _wrap_sendmail_result(result: dict[str, tuple[int, bytes]]) -> Dict:
    out = Dict()
    for k, (code, msg) in result.items():
        out.at_put(Str(k), Tuple(Int(code), Bytes(msg)))
    return out


class _SMTPBase(Object):
    """Shared scaffolding for the `SMTP` / `SMTP_SSL` / `LMTP` wrappers.

    Construction wraps the underlying impl; the full method surface is
    inherited from the concrete subclasses below.
    """

    __slots__ = ("_impl",)
    _impl: Any

    def connect(self, host: Str | None = None, port: Int | None = None) -> Tuple:
        kwargs: dict[str, Any] = {}
        if host is not None:
            kwargs["host"] = host._value
        if port is not None:
            kwargs["port"] = port._value
        return _wrap_helo_tuple(self._impl.connect(**kwargs))

    def helo(self, name: Str | None = None) -> Tuple:
        return _wrap_helo_tuple(self._impl.helo(_opt_str(name, "")))

    def ehlo(self, name: Str | None = None) -> Tuple:
        return _wrap_helo_tuple(self._impl.ehlo(_opt_str(name, "")))

    def has_extn(self, name: Str) -> bool:
        return self._impl.has_extn(name._value)

    def docmd(self, cmd: Str, args: Str | None = None) -> Tuple:
        return _wrap_helo_tuple(self._impl.docmd(cmd._value, _opt_str(args, "")))

    def noop(self) -> Tuple:
        return _wrap_helo_tuple(self._impl.noop())

    def verify(self, address: Str) -> Tuple:
        return _wrap_helo_tuple(self._impl.verify(address._value))

    def expn(self, address: Str) -> Tuple:
        return _wrap_helo_tuple(self._impl.expn(address._value))

    def rset(self) -> Tuple:
        return _wrap_helo_tuple(self._impl.rset())

    def starttls(self) -> Tuple:
        return _wrap_helo_tuple(self._impl.starttls())

    def login(self, user: Str, password: Str) -> Tuple:
        return _wrap_helo_tuple(self._impl.login(user._value, password._value))

    def sendmail(
        self,
        from_addr: Str,
        to_addrs: Str | List,
        msg: Str | Bytes,
        mail_options: List | None = None,
        rcpt_options: List | None = None,
    ) -> Dict:
        if isinstance(to_addrs, List):
            recipients: Any = [
                addr._value if isinstance(addr, Str) else addr for addr in to_addrs
            ]
        else:
            recipients = to_addrs._value
        kwargs: dict[str, Any] = {}
        if mail_options is not None:
            kwargs["mail_options"] = [
                o._value if isinstance(o, Str) else o for o in mail_options
            ]
        if rcpt_options is not None:
            kwargs["rcpt_options"] = [
                o._value if isinstance(o, Str) else o for o in rcpt_options
            ]
        return _wrap_sendmail_result(
            self._impl.sendmail(from_addr._value, recipients, msg._value, **kwargs)
        )

    def send_message(
        self,
        msg: Any,
        from_addr: Str | None = None,
        to_addrs: Str | List | None = None,
    ) -> Dict:
        kwargs: dict[str, Any] = {}
        if from_addr is not None:
            kwargs["from_addr"] = from_addr._value
        if to_addrs is not None:
            if isinstance(to_addrs, List):
                kwargs["to_addrs"] = [
                    a._value if isinstance(a, Str) else a for a in to_addrs
                ]
            else:
                kwargs["to_addrs"] = to_addrs._value
        return _wrap_sendmail_result(self._impl.send_message(msg, **kwargs))

    def set_debuglevel(self, level: Int) -> NoneClass:
        self._impl.set_debuglevel(level._value)
        return none

    def quit(self) -> Tuple:
        return _wrap_helo_tuple(self._impl.quit())

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._impl.__exit__(exc_type, exc_value, traceback)


class SMTP(_SMTPBase):
    """Wraps Python's `smtplib.SMTP` — RFC 5321 SMTP client."""

    def __init__(
        self,
        host: Str | None = None,
        port: Int | None = None,
        local_hostname: Str | None = None,
        timeout: Int | None = None,
        source_address: Tuple | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if host is not None:
            kwargs["host"] = host._value
        if port is not None:
            kwargs["port"] = port._value
        if local_hostname is not None:
            kwargs["local_hostname"] = local_hostname._value
        if timeout is not None:
            kwargs["timeout"] = timeout._value
        if source_address is not None:
            host_part = source_address.at(Int(0))
            port_part = source_address.at(Int(1))
            kwargs["source_address"] = (
                host_part._value if isinstance(host_part, Str) else host_part,
                port_part._value if isinstance(port_part, Int) else port_part,
            )
        self._impl = _smtplib.SMTP(**kwargs)


class SMTP_SSL(_SMTPBase):
    """Wraps Python's `smtplib.SMTP_SSL` — SMTP over TLS."""

    def __init__(
        self,
        host: Str | None = None,
        port: Int | None = None,
        local_hostname: Str | None = None,
        timeout: Int | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if host is not None:
            kwargs["host"] = host._value
        if port is not None:
            kwargs["port"] = port._value
        if local_hostname is not None:
            kwargs["local_hostname"] = local_hostname._value
        if timeout is not None:
            kwargs["timeout"] = timeout._value
        self._impl = _smtplib.SMTP_SSL(**kwargs)


class LMTP(_SMTPBase):
    """Wraps Python's `smtplib.LMTP` — Local Mail Transfer Protocol."""

    def __init__(
        self,
        host: Str | None = None,
        port: Int | None = None,
        local_hostname: Str | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {}
        if host is not None:
            kwargs["host"] = host._value
        if port is not None:
            kwargs["port"] = port._value
        if local_hostname is not None:
            kwargs["local_hostname"] = local_hostname._value
        self._impl = _smtplib.LMTP(**kwargs)


class Smtplib:
    """Namespace mirroring Python's `smtplib` module."""

    SMTP: ClassVar[type[SMTP]] = SMTP
    SMTP_SSL: ClassVar[type[SMTP_SSL]] = SMTP_SSL
    LMTP: ClassVar[type[LMTP]] = LMTP

    # Constants.
    SMTP_PORT: ClassVar[Int] = Int(_smtplib.SMTP_PORT)
    SMTP_SSL_PORT: ClassVar[Int] = Int(_smtplib.SMTP_SSL_PORT)
    LMTP_PORT: ClassVar[Int] = Int(_smtplib.LMTP_PORT)
    CRLF: ClassVar[Str] = Str(_smtplib.CRLF)
    bCRLF: ClassVar[Bytes] = Bytes(_smtplib.bCRLF)

    # Errors.
    SMTPException: ClassVar[type[Exception]] = _smtplib.SMTPException
    SMTPServerDisconnected: ClassVar[type[Exception]] = _smtplib.SMTPServerDisconnected
    SMTPResponseException: ClassVar[type[Exception]] = _smtplib.SMTPResponseException
    SMTPSenderRefused: ClassVar[type[Exception]] = _smtplib.SMTPSenderRefused
    SMTPRecipientsRefused: ClassVar[type[Exception]] = _smtplib.SMTPRecipientsRefused
    SMTPDataError: ClassVar[type[Exception]] = _smtplib.SMTPDataError
    SMTPConnectError: ClassVar[type[Exception]] = _smtplib.SMTPConnectError
    SMTPHeloError: ClassVar[type[Exception]] = _smtplib.SMTPHeloError
    SMTPNotSupportedError: ClassVar[type[Exception]] = _smtplib.SMTPNotSupportedError
    SMTPAuthenticationError: ClassVar[type[Exception]] = (
        _smtplib.SMTPAuthenticationError
    )
