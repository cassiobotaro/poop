from __future__ import annotations

import email as _email
import email.message as _email_message
import email.policy as _email_policy
import email.utils as _email_utils
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _unwrap_policy(policy: Any) -> Any:
    """Accept either a real Python policy object or a POOP-wrapped one."""
    if policy is None or isinstance(policy, NoneClass):
        return _email_policy.default
    return policy


class EmailMessage(Object):
    """Wraps Python's `email.message.EmailMessage` — a modern MIME message."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any = None) -> None:
        if impl is None:
            self._impl = _email_message.EmailMessage(policy=_email_policy.default)
        else:
            self._impl = impl

    def set_content(
        self, content: Str | Bytes, subtype: Str | None = None
    ) -> NoneClass:
        sub = "plain" if subtype is None else subtype._value
        if isinstance(content, Bytes):
            self._impl.set_content(content._value, subtype=sub)
        else:
            self._impl.set_content(content._value, subtype=sub)
        return none

    def get_content(self) -> Str | Bytes:
        result = self._impl.get_content()
        if isinstance(result, bytes):
            return Bytes(result)
        return Str(result)

    def add_alternative(
        self, content: Str | Bytes, subtype: Str | None = None
    ) -> NoneClass:
        sub = "plain" if subtype is None else subtype._value
        self._impl.add_alternative(content._value, subtype=sub)
        return none

    def add_attachment(
        self,
        content: Bytes,
        maintype: Str,
        subtype: Str,
        filename: Str | None = None,
    ) -> NoneClass:
        if filename is None:
            self._impl.add_attachment(
                content._value, maintype=maintype._value, subtype=subtype._value
            )
        else:
            self._impl.add_attachment(
                content._value,
                maintype=maintype._value,
                subtype=subtype._value,
                filename=filename._value,
            )
        return none

    def is_multipart(self) -> Boolean:
        return true if self._impl.is_multipart() else false

    def at(self, key: Str) -> Str | NoneClass:
        val = self._impl.get(key._value)
        return none if val is None else Str(str(val))

    def at_put(self, key: Str, value: Str) -> NoneClass:
        self._impl[key._value] = value._value
        return none

    def keys(self) -> List:
        return List(*(Str(k) for k in self._impl.keys()))

    def values(self) -> List:
        return List(*(Str(str(v)) for v in self._impl.values()))

    def items(self) -> List:
        return List(*(Tuple(Str(k), Str(str(v))) for k, v in self._impl.items()))

    def as_string(self) -> Str:
        return Str(self._impl.as_string())

    def as_bytes(self) -> Bytes:
        return Bytes(self._impl.as_bytes())

    def iter_parts(self) -> List:
        return List(*(EmailMessage(p) for p in self._impl.iter_parts()))

    def iter_attachments(self) -> List:
        return List(*(EmailMessage(p) for p in self._impl.iter_attachments()))

    def get_body(self, preferencelist: List | None = None) -> EmailMessage | NoneClass:
        if preferencelist is None:
            body = self._impl.get_body()
        else:
            prefs = []
            for elem in preferencelist:
                if not isinstance(elem, Str):
                    raise TypeError("preferencelist must be List[Str]")
                prefs.append(elem._value)
            body = self._impl.get_body(preferencelist=prefs)
        return none if body is None else EmailMessage(body)

    def __str__(self) -> str:
        return self._impl.as_string()

    __repr__ = __str__


class EmailUtils:
    """Namespace mirroring Python's `email.utils` module."""

    @staticmethod
    def parseaddr(address: Str) -> Tuple:
        name, addr = _email_utils.parseaddr(address._value)
        return Tuple(Str(name), Str(addr))

    @staticmethod
    def formataddr(pair: Tuple, charset: Str | None = None) -> Str:
        if pair.len()._value != 2:
            raise ValueError("formataddr expects a Tuple(name, addr)")
        name = pair.at(Int(0))
        addr = pair.at(Int(1))
        if not isinstance(name, Str) or not isinstance(addr, Str):
            raise TypeError("formataddr expects Tuple(Str, Str)")
        cs = "utf-8" if charset is None else charset._value
        return Str(_email_utils.formataddr((name._value, addr._value), charset=cs))

    @staticmethod
    def getaddresses(fieldvalues: List) -> List:
        raw = []
        for elem in fieldvalues:
            if not isinstance(elem, Str):
                raise TypeError("getaddresses expects List[Str]")
            raw.append(elem._value)
        return List(*(Tuple(Str(n), Str(a)) for n, a in _email_utils.getaddresses(raw)))

    @staticmethod
    def parsedate(date: Str) -> Tuple | NoneClass:
        parsed = _email_utils.parsedate(date._value)
        if parsed is None:
            return none
        return Tuple(*(Int(x) for x in parsed))

    @staticmethod
    def formatdate(
        timeval: Int | None = None,
        localtime: Boolean | None = None,
        usegmt: Boolean | None = None,
    ) -> Str:
        ts = None if timeval is None else timeval._value
        lt = False if localtime is None else bool(localtime)
        ug = False if usegmt is None else bool(usegmt)
        return Str(_email_utils.formatdate(timeval=ts, localtime=lt, usegmt=ug))

    @staticmethod
    def make_msgid(idstring: Str | None = None, domain: Str | None = None) -> Str:
        ids = None if idstring is None else idstring._value
        dom = None if domain is None else domain._value
        return Str(_email_utils.make_msgid(idstring=ids, domain=dom))


class EmailPolicy:
    """Namespace mirroring Python's `email.policy` module — preset policies."""

    default: ClassVar[Any] = _email_policy.default
    SMTP: ClassVar[Any] = _email_policy.SMTP
    SMTPUTF8: ClassVar[Any] = _email_policy.SMTPUTF8
    HTTP: ClassVar[Any] = _email_policy.HTTP
    strict: ClassVar[Any] = _email_policy.strict
    compat32: ClassVar[Any] = _email_policy.compat32


class Email:
    """Namespace mirroring Python's `email` package."""

    EmailMessage: ClassVar[type[EmailMessage]] = EmailMessage
    utils: ClassVar[type[EmailUtils]] = EmailUtils
    policy: ClassVar[type[EmailPolicy]] = EmailPolicy

    @staticmethod
    def message_from_string(s: Str, policy: Any | None = None) -> EmailMessage:
        return EmailMessage(
            _email.message_from_string(
                s._value,
                _class=_email_message.EmailMessage,
                policy=_unwrap_policy(policy),
            )
        )

    @staticmethod
    def message_from_bytes(b: Bytes, policy: Any | None = None) -> EmailMessage:
        return EmailMessage(
            _email.message_from_bytes(
                b._value,
                _class=_email_message.EmailMessage,
                policy=_unwrap_policy(policy),
            )
        )
