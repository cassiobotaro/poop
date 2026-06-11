from __future__ import annotations

import ssl as _ssl
from typing import Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _kwargs_from, _opt_path_or_str, _path_or_str
from poop.types.boolean import Boolean, to_boolean
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.socket import Socket
from poop.types.string import Str


class SSLContext(_ImplWrapperMixin, Object):
    """Wraps Python's `ssl.SSLContext`."""

    __slots__ = ("_impl",)

    def __init__(self, protocol: Int | NoneClass | None = None) -> None:
        # Mirror CPython: the constructor takes a protocol constant
        # (PROTOCOL_TLS_CLIENT/PROTOCOL_TLS_SERVER), defaulting to the
        # TLS client protocol. A raw ssl.SSLContext is wrapped via
        # _from_impl (create_default_context), never the public ctor.
        if protocol is None or isinstance(protocol, NoneClass):
            self._impl = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
        else:
            self._impl = _ssl.SSLContext(protocol._value)

    def load_cert_chain(
        self,
        certfile: Path | Str,
        keyfile: Path | Str | None = None,
        password: Str | None = None,
    ) -> NoneClass:
        cf = _path_or_str(certfile)
        kf = _opt_path_or_str(keyfile)
        pw = None if password is None else password._value
        self._impl.load_cert_chain(cf, kf, pw)
        return none

    def load_verify_locations(
        self,
        cafile: Path | Str | None = None,
        capath: Path | Str | None = None,
        cadata: Str | None = None,
    ) -> NoneClass:
        cf = _opt_path_or_str(cafile)
        cp = _opt_path_or_str(capath)
        cd = None if cadata is None else cadata._value
        self._impl.load_verify_locations(cf, cp, cd)
        return none

    def load_default_certs(self) -> NoneClass:
        self._impl.load_default_certs()
        return none

    def set_ciphers(self, ciphers: Str) -> NoneClass:
        self._impl.set_ciphers(ciphers._value)
        return none

    def get_ciphers(self) -> List:
        from poop.types._bridge import to_poop

        return List(*(to_poop(cipher) for cipher in self._impl.get_ciphers()))

    @property
    def check_hostname(self) -> Boolean:
        return to_boolean(self._impl.check_hostname)

    @check_hostname.setter
    def check_hostname(self, value: Boolean) -> None:
        self._impl.check_hostname = bool(value)

    @property
    def verify_mode(self) -> Int:
        return Int(int(self._impl.verify_mode))

    @verify_mode.setter
    def verify_mode(self, value: Int) -> None:
        self._impl.verify_mode = _ssl.VerifyMode(value._value)

    def wrap_socket(
        self,
        sock: Socket,
        server_hostname: Str | None = None,
        server_side: Boolean | None = None,
    ) -> Socket:
        kwargs = _kwargs_from(server_hostname=server_hostname)
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

    # Purpose enum members (raw int values).
    PURPOSE_SERVER_AUTH: ClassVar[Any] = _ssl.Purpose.SERVER_AUTH
    PURPOSE_CLIENT_AUTH: ClassVar[Any] = _ssl.Purpose.CLIENT_AUTH

    # OP_* options (bitmask flags on SSLContext.options).
    OP_ALL: ClassVar[Int] = Int(int(_ssl.OP_ALL))
    OP_NO_COMPRESSION: ClassVar[Int] = Int(int(_ssl.OP_NO_COMPRESSION))
    OP_NO_TICKET: ClassVar[Int] = Int(int(_ssl.OP_NO_TICKET))
    OP_NO_SSLv2: ClassVar[Int] = Int(int(_ssl.OP_NO_SSLv2))
    OP_NO_SSLv3: ClassVar[Int] = Int(int(_ssl.OP_NO_SSLv3))
    OP_NO_TLSv1: ClassVar[Int] = Int(int(_ssl.OP_NO_TLSv1))
    OP_NO_TLSv1_1: ClassVar[Int] = Int(int(_ssl.OP_NO_TLSv1_1))
    OP_NO_TLSv1_2: ClassVar[Int] = Int(int(_ssl.OP_NO_TLSv1_2))
    OP_NO_TLSv1_3: ClassVar[Int] = Int(int(_ssl.OP_NO_TLSv1_3))
    OP_CIPHER_SERVER_PREFERENCE: ClassVar[Int] = Int(
        int(_ssl.OP_CIPHER_SERVER_PREFERENCE)
    )
    OP_SINGLE_DH_USE: ClassVar[Int] = Int(int(_ssl.OP_SINGLE_DH_USE))
    OP_SINGLE_ECDH_USE: ClassVar[Int] = Int(int(_ssl.OP_SINGLE_ECDH_USE))

    # HAS_* capability flags.
    HAS_SSLv2: ClassVar[Boolean] = to_boolean(_ssl.HAS_SSLv2)
    HAS_SSLv3: ClassVar[Boolean] = to_boolean(_ssl.HAS_SSLv3)
    HAS_TLSv1: ClassVar[Boolean] = to_boolean(_ssl.HAS_TLSv1)
    HAS_TLSv1_1: ClassVar[Boolean] = to_boolean(_ssl.HAS_TLSv1_1)
    HAS_TLSv1_2: ClassVar[Boolean] = to_boolean(_ssl.HAS_TLSv1_2)
    HAS_TLSv1_3: ClassVar[Boolean] = to_boolean(_ssl.HAS_TLSv1_3)
    HAS_ALPN: ClassVar[Boolean] = to_boolean(_ssl.HAS_ALPN)

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
    CertificateError: ClassVar[type[BaseException]] = _ssl.CertificateError

    @staticmethod
    def DER_cert_to_PEM_cert(der_cert_bytes: Bytes, /) -> Str:
        return Str(_ssl.DER_cert_to_PEM_cert(der_cert_bytes._value))

    @staticmethod
    def PEM_cert_to_DER_cert(pem_cert_string: Str, /) -> Bytes:
        return Bytes(_ssl.PEM_cert_to_DER_cert(pem_cert_string._value))

    @staticmethod
    def get_server_certificate(
        addr: Any,
        ssl_version: Any = None,
        ca_certs: Str | None = None,
        timeout: Any = None,
    ) -> Str:
        kwargs: dict[str, Any] = {}
        if ssl_version is not None:
            kwargs["ssl_version"] = ssl_version
        if ca_certs is not None:
            kwargs["ca_certs"] = ca_certs._value
        if timeout is not None:
            kwargs["timeout"] = timeout
        return Str(_ssl.get_server_certificate(addr, **kwargs))

    @staticmethod
    def create_default_context(
        purpose: Any = _ssl.Purpose.SERVER_AUTH,
        *,
        cafile: Path | Str | None = None,
        capath: Path | Str | None = None,
        cadata: Str | Bytes | None = None,
    ) -> SSLContext:
        # `purpose` is an `ssl.Purpose` enum value; POOP exposes the
        # enum members directly (`SSL.PROTOCOL_TLS_SERVER` etc.) but
        # accepts the raw CPython value here as a passthrough.
        cf = _opt_path_or_str(cafile)
        cp = _opt_path_or_str(capath)
        cd = None if cadata is None else cadata._value
        return SSLContext._from_impl(
            _ssl.create_default_context(purpose, cafile=cf, capath=cp, cadata=cd)
        )
