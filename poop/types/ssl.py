from __future__ import annotations

import ssl as _ssl
from typing import Any, ClassVar

from poop.types.boolean import Boolean, false, true
from poop.types.int import Int
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.socket import Socket
from poop.types.string import Str


class SSLContext(Object):
    """Wraps Python's `ssl.SSLContext`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any = None) -> None:
        if impl is None:
            self._impl = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
        else:
            self._impl = impl

    def load_cert_chain(
        self,
        certfile: Path | Str,
        keyfile: Path | Str | None = None,
        password: Str | None = None,
    ) -> NoneClass:
        cf = certfile._value if isinstance(certfile, Str) else str(certfile)
        kf = (
            None
            if keyfile is None
            else (keyfile._value if isinstance(keyfile, Str) else str(keyfile))
        )
        pw = None if password is None else password._value
        self._impl.load_cert_chain(cf, kf, pw)
        return none

    def load_verify_locations(
        self,
        cafile: Path | Str | None = None,
        capath: Path | Str | None = None,
        cadata: Str | None = None,
    ) -> NoneClass:
        cf = (
            None
            if cafile is None
            else (cafile._value if isinstance(cafile, Str) else str(cafile))
        )
        cp = (
            None
            if capath is None
            else (capath._value if isinstance(capath, Str) else str(capath))
        )
        cd = None if cadata is None else cadata._value
        self._impl.load_verify_locations(cf, cp, cd)
        return none

    def load_default_certs(self) -> NoneClass:
        self._impl.load_default_certs()
        return none

    def set_ciphers(self, ciphers: Str) -> NoneClass:
        self._impl.set_ciphers(ciphers._value)
        return none

    def get_ciphers(self) -> Any:
        return self._impl.get_ciphers()

    @property
    def check_hostname(self) -> Boolean:
        return true if self._impl.check_hostname else false

    def set_check_hostname(self, flag: Boolean) -> NoneClass:
        self._impl.check_hostname = bool(flag)
        return none

    @property
    def verify_mode(self) -> Int:
        return Int(int(self._impl.verify_mode))

    def set_verify_mode(self, mode: Int) -> NoneClass:
        self._impl.verify_mode = _ssl.VerifyMode(mode._value)
        return none

    def wrap_socket(
        self,
        sock: Socket,
        server_hostname: Str | None = None,
        server_side: Boolean | None = None,
    ) -> Socket:
        kwargs: dict[str, Any] = {}
        if server_hostname is not None:
            kwargs["server_hostname"] = server_hostname._value
        if server_side is not None:
            kwargs["server_side"] = bool(server_side)
        wrapped = self._impl.wrap_socket(sock._impl, **kwargs)
        return Socket(impl=wrapped)


class SSL:
    """Namespace mirroring Python's `ssl` module."""

    SSLContext: ClassVar[type[SSLContext]] = SSLContext

    # Protocol constants
    PROTOCOL_TLS_CLIENT: ClassVar[Int] = Int(int(_ssl.PROTOCOL_TLS_CLIENT))
    PROTOCOL_TLS_SERVER: ClassVar[Int] = Int(int(_ssl.PROTOCOL_TLS_SERVER))

    # Verify modes
    CERT_NONE: ClassVar[Int] = Int(int(_ssl.CERT_NONE))
    CERT_OPTIONAL: ClassVar[Int] = Int(int(_ssl.CERT_OPTIONAL))
    CERT_REQUIRED: ClassVar[Int] = Int(int(_ssl.CERT_REQUIRED))

    # Errors
    SSLError: ClassVar[type[BaseException]] = _ssl.SSLError
    SSLZeroReturnError: ClassVar[type[BaseException]] = _ssl.SSLZeroReturnError
    SSLWantReadError: ClassVar[type[BaseException]] = _ssl.SSLWantReadError
    SSLWantWriteError: ClassVar[type[BaseException]] = _ssl.SSLWantWriteError
    SSLSyscallError: ClassVar[type[BaseException]] = _ssl.SSLSyscallError
    SSLEOFError: ClassVar[type[BaseException]] = _ssl.SSLEOFError
    SSLCertVerificationError: ClassVar[type[BaseException]] = (
        _ssl.SSLCertVerificationError
    )

    @staticmethod
    def create_default_context(
        cafile: Path | Str | None = None,
        capath: Path | Str | None = None,
    ) -> SSLContext:
        cf = (
            None
            if cafile is None
            else (cafile._value if isinstance(cafile, Str) else str(cafile))
        )
        cp = (
            None
            if capath is None
            else (capath._value if isinstance(capath, Str) else str(capath))
        )
        return SSLContext(impl=_ssl.create_default_context(cafile=cf, capath=cp))
