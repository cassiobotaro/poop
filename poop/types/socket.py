from __future__ import annotations

import socket as _socket
from typing import Any, ClassVar, Self

from poop.types._unwrap import _is_absent
from poop.types.boolean import Boolean, false, to_boolean
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _unwrap_address(addr: Any) -> Any:
    if isinstance(addr, Tuple):
        return tuple(_unwrap_address(x) for x in addr)
    if isinstance(addr, (Str, Int)):
        return addr._value
    return addr


def _wrap_address(addr: Any) -> Tuple | Str | Bytes:
    if isinstance(addr, tuple):
        wrapped: list[Any] = []
        for item in addr:
            if isinstance(item, str):
                wrapped.append(Str(item))
            elif isinstance(item, int):
                wrapped.append(Int(item))
            else:
                wrapped.append(item)
        return Tuple(*wrapped)
    if isinstance(addr, str):
        return Str(addr)
    if isinstance(addr, (bytes, bytearray)):
        # AF_UNIX abstract namespace addresses come back as bytes on Linux.
        return Bytes(bytes(addr))
    return addr


class Socket(Object):
    """Wraps Python's `socket.socket` — TCP/UDP/Unix sockets."""

    __slots__ = ("_impl",)

    def __init__(
        self,
        family: Int | Any | None = None,
        type: Int | None = None,
        proto: Int | None = None,
        impl: Any = None,
    ) -> None:
        if impl is not None:
            self._impl = impl
            return
        f = _socket.AF_INET if family is None else family._value
        t = _socket.SOCK_STREAM if type is None else type._value
        p = 0 if proto is None else proto._value
        self._impl = _socket.socket(f, t, p)

    def bind(self, address: Tuple | Str) -> NoneClass:
        self._impl.bind(_unwrap_address(address))
        return none

    def listen(self, backlog: Int | None = None) -> NoneClass:
        if backlog is None:
            self._impl.listen()
        else:
            self._impl.listen(backlog._value)
        return none

    def accept(self) -> Tuple:
        sock, addr = self._impl.accept()
        return Tuple(Socket(impl=sock), _wrap_address(addr))

    def connect(self, address: Tuple | Str) -> NoneClass:
        self._impl.connect(_unwrap_address(address))
        return none

    def connect_ex(self, address: Tuple | Str) -> Int:
        return Int(self._impl.connect_ex(_unwrap_address(address)))

    def send(self, data: Bytes, flags: Int | None = None) -> Int:
        f = 0 if flags is None else flags._value
        return Int(self._impl.send(data._value, f))

    def sendall(self, data: Bytes, flags: Int | None = None) -> NoneClass:
        f = 0 if flags is None else flags._value
        self._impl.sendall(data._value, f)
        return none

    def sendto(self, data: Bytes, address: Tuple | Str) -> Int:
        return Int(self._impl.sendto(data._value, _unwrap_address(address)))

    def recv(self, bufsize: Int, flags: Int | None = None) -> Bytes:
        f = 0 if flags is None else flags._value
        return Bytes(self._impl.recv(bufsize._value, f))

    def recvfrom(self, bufsize: Int) -> Tuple:
        data, addr = self._impl.recvfrom(bufsize._value)
        return Tuple(Bytes(data), _wrap_address(addr))

    def close(self) -> NoneClass:
        self._impl.close()
        return none

    def shutdown(self, how: Int) -> NoneClass:
        self._impl.shutdown(how._value)
        return none

    def setsockopt(self, level: Int, optname: Int, value: Int | Bytes) -> NoneClass:
        v = value._value
        self._impl.setsockopt(level._value, optname._value, v)
        return none

    def getsockopt(self, level: Int, optname: Int) -> Int:
        return Int(self._impl.getsockopt(level._value, optname._value))

    def settimeout(self, value: Float | Int | NoneClass | None) -> NoneClass:
        if value is None or isinstance(value, NoneClass):
            self._impl.settimeout(None)
        else:
            self._impl.settimeout(value._value)
        return none

    def gettimeout(self) -> Float | NoneClass:
        result = self._impl.gettimeout()
        return none if result is None else Float(result)

    def setblocking(self, flag: Boolean) -> NoneClass:
        self._impl.setblocking(bool(flag))
        return none

    def fileno(self) -> Int:
        return Int(self._impl.fileno())

    def getsockname(self) -> Tuple | Str | Bytes:
        return _wrap_address(self._impl.getsockname())

    def getpeername(self) -> Tuple | Str | Bytes:
        return _wrap_address(self._impl.getpeername())

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_exc: object) -> None:
        self._impl.close()


def _wrap_sockaddr_item(value: Any) -> Any:
    if isinstance(value, str):
        return Str(value)
    if isinstance(value, int):
        return Int(value)
    return value


def _unwrap_sockaddr_item(value: Any) -> Any:
    if isinstance(value, Str):
        return value._value
    if isinstance(value, Int):
        return value._value
    return value


class SocketNamespace:
    """Namespace mirroring Python's `socket` module."""

    Socket: ClassVar[type[Socket]] = Socket
    SocketType: ClassVar[type[_socket.socket]] = _socket.socket

    # getaddrinfo / NI flags
    AI_PASSIVE: ClassVar[Int] = Int(_socket.AI_PASSIVE)
    AI_CANONNAME: ClassVar[Int] = Int(_socket.AI_CANONNAME)
    AI_NUMERICHOST: ClassVar[Int] = Int(_socket.AI_NUMERICHOST)
    AI_NUMERICSERV: ClassVar[Int] = Int(_socket.AI_NUMERICSERV)
    NI_NUMERICHOST: ClassVar[Int] = Int(_socket.NI_NUMERICHOST)
    NI_NUMERICSERV: ClassVar[Int] = Int(_socket.NI_NUMERICSERV)
    NI_NOFQDN: ClassVar[Int] = Int(_socket.NI_NOFQDN)
    NI_NAMEREQD: ClassVar[Int] = Int(_socket.NI_NAMEREQD)
    NI_DGRAM: ClassVar[Int] = Int(_socket.NI_DGRAM)

    # Address families
    AF_INET: ClassVar[Int] = Int(_socket.AF_INET)
    AF_INET6: ClassVar[Int] = Int(_socket.AF_INET6)
    AF_UNIX: ClassVar[Int | NoneClass] = (
        Int(_socket.AF_UNIX) if hasattr(_socket, "AF_UNIX") else none
    )
    AF_UNSPEC: ClassVar[Int] = Int(_socket.AF_UNSPEC)

    # Socket types
    SOCK_STREAM: ClassVar[Int] = Int(_socket.SOCK_STREAM)
    SOCK_DGRAM: ClassVar[Int] = Int(_socket.SOCK_DGRAM)
    SOCK_RAW: ClassVar[Int] = Int(_socket.SOCK_RAW)

    # Common socket options
    SOL_SOCKET: ClassVar[Int] = Int(_socket.SOL_SOCKET)
    SO_REUSEADDR: ClassVar[Int] = Int(_socket.SO_REUSEADDR)
    SO_KEEPALIVE: ClassVar[Int] = Int(_socket.SO_KEEPALIVE)
    SO_BROADCAST: ClassVar[Int] = Int(_socket.SO_BROADCAST)

    # Shutdown how-values
    SHUT_RD: ClassVar[Int] = Int(_socket.SHUT_RD)
    SHUT_WR: ClassVar[Int] = Int(_socket.SHUT_WR)
    SHUT_RDWR: ClassVar[Int] = Int(_socket.SHUT_RDWR)

    # Error classes
    error: ClassVar[type[BaseException]] = _socket.error
    herror: ClassVar[type[BaseException]] = _socket.herror
    gaierror: ClassVar[type[BaseException]] = _socket.gaierror
    timeout: ClassVar[type[BaseException]] = _socket.timeout

    @staticmethod
    def gethostname() -> Str:
        return Str(_socket.gethostname())

    @staticmethod
    def gethostbyname(host: Str) -> Str:
        return Str(_socket.gethostbyname(host._value))

    @staticmethod
    def gethostbyname_ex(host: Str) -> Tuple:
        name, aliases, addrs = _socket.gethostbyname_ex(host._value)
        return Tuple(
            Str(name),
            List(*(Str(a) for a in aliases)),
            List(*(Str(a) for a in addrs)),
        )

    @staticmethod
    def gethostbyaddr(addr: Str) -> Tuple:
        name, aliases, addrs = _socket.gethostbyaddr(addr._value)
        return Tuple(
            Str(name),
            List(*(Str(a) for a in aliases)),
            List(*(Str(a) for a in addrs)),
        )

    @staticmethod
    def getfqdn(name: Str | None = None) -> Str:
        if name is None:
            return Str(_socket.getfqdn())
        return Str(_socket.getfqdn(name._value))

    @staticmethod
    def has_dualstack_ipv6() -> Boolean:
        return to_boolean(_socket.has_dualstack_ipv6())

    @staticmethod
    def getservbyname(servicename: Str, protocolname: Str | None = None) -> Int:
        if protocolname is None:
            return Int(_socket.getservbyname(servicename._value))
        return Int(_socket.getservbyname(servicename._value, protocolname._value))

    @staticmethod
    def getservbyport(port: Int, protocolname: Str | None = None) -> Str:
        if protocolname is None:
            return Str(_socket.getservbyport(port._value))
        return Str(_socket.getservbyport(port._value, protocolname._value))

    @staticmethod
    def htons(integer: Int, /) -> Int:
        return Int(_socket.htons(integer._value))

    @staticmethod
    def htonl(integer: Int, /) -> Int:
        return Int(_socket.htonl(integer._value))

    @staticmethod
    def ntohs(integer: Int, /) -> Int:
        return Int(_socket.ntohs(integer._value))

    @staticmethod
    def ntohl(integer: Int, /) -> Int:
        return Int(_socket.ntohl(integer._value))

    @staticmethod
    def inet_aton(ip_addr: Str, /) -> Bytes:
        return Bytes(_socket.inet_aton(ip_addr._value))

    @staticmethod
    def inet_ntoa(packed_ip: Bytes) -> Str:
        return Str(_socket.inet_ntoa(packed_ip._value))

    @staticmethod
    def inet_pton(family: Int, ip_string: Str) -> Bytes:
        return Bytes(_socket.inet_pton(family._value, ip_string._value))

    @staticmethod
    def inet_ntop(family: Int, packed_ip: Bytes) -> Str:
        return Str(_socket.inet_ntop(family._value, packed_ip._value))

    @staticmethod
    def create_connection(
        address: Tuple,
        timeout: Float | Int | NoneClass | None = None,
        source_address: Tuple | NoneClass | None = None,
        *,
        all_errors: Boolean = false,
    ) -> Socket:
        addr = _unwrap_address(address)
        kwargs: dict[str, Any] = {"all_errors": bool(all_errors)}
        if not _is_absent(timeout):
            kwargs["timeout"] = timeout._value
        if not _is_absent(source_address):
            kwargs["source_address"] = _unwrap_address(source_address)
        sock = _socket.create_connection(addr, **kwargs)
        return Socket(impl=sock)

    @staticmethod
    def create_server(
        address: Tuple,
        *,
        family: Int = Int(_socket.AF_INET),
        backlog: Int | NoneClass | None = None,
        reuse_port: Boolean = false,
        dualstack_ipv6: Boolean = false,
    ) -> Socket:
        addr = _unwrap_address(address)
        kwargs: dict[str, Any] = {
            "family": family._value,
            "reuse_port": bool(reuse_port),
            "dualstack_ipv6": bool(dualstack_ipv6),
        }
        if not _is_absent(backlog):
            kwargs["backlog"] = backlog._value
        sock = _socket.create_server(addr, **kwargs)
        return Socket(impl=sock)

    @staticmethod
    def getaddrinfo(
        host: Str | NoneClass | None,
        port: Int | Str | NoneClass | None,
        family: Int | None = None,
        type: Int | None = None,
        proto: Int | None = None,
        flags: Int | None = None,
    ) -> List:
        h = None if host is None or isinstance(host, NoneClass) else host._value
        if port is None or isinstance(port, NoneClass):
            p: Any = None
        else:
            p = port._value
        results = _socket.getaddrinfo(
            h,
            p,
            0 if family is None else family._value,
            0 if type is None else type._value,
            0 if proto is None else proto._value,
            0 if flags is None else flags._value,
        )
        out: list[Tuple] = []
        for fam, sock_type, prot, canonname, sockaddr in results:
            sa_items = tuple(_wrap_sockaddr_item(v) for v in sockaddr)
            out.append(
                Tuple(
                    Int(fam),
                    Int(sock_type),
                    Int(prot),
                    Str(canonname),
                    Tuple(*sa_items),
                )
            )
        return List(*out)

    @staticmethod
    def getnameinfo(sockaddr: Tuple, flags: Int) -> Tuple:
        raw = tuple(_unwrap_sockaddr_item(v) for v in sockaddr._items)
        host, port = _socket.getnameinfo(raw, flags._value)
        return Tuple(Str(host), Str(port))

    @staticmethod
    def if_indextoname(index: Int) -> Str:
        return Str(_socket.if_indextoname(index._value))

    @staticmethod
    def if_nametoindex(name: Str) -> Int:
        return Int(_socket.if_nametoindex(name._value))

    @staticmethod
    def if_nameindex() -> List:
        return List(*(Tuple(Int(i), Str(n)) for i, n in _socket.if_nameindex()))
