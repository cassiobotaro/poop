from __future__ import annotations

import ipaddress as _ipaddress
from collections.abc import Iterator
from typing import Any, ClassVar

from poop.types._impl_wrapper import _ImplWrapperMixin
from poop.types._unwrap import _b, _kwargs_from
from poop.types._value_eq import _ValueEqMixin
from poop.types.boolean import Boolean, to_boolean
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.string import Str
from poop.types.tuple import Tuple


def _addr_arg(value: IPv4Address | IPv6Address | Str | Int | Bytes) -> Any:
    if isinstance(value, IPv4Address | IPv6Address):
        return value._impl
    if isinstance(value, Str | Bytes):
        return value._value
    if isinstance(value, Int):
        return value._value
    return value


def _wrap_address(impl: Any) -> IPv4Address | IPv6Address:
    if isinstance(impl, _ipaddress.IPv4Address):
        return IPv4Address._from_impl(impl)
    return IPv6Address._from_impl(impl)


def _wrap_network(impl: Any) -> IPv4Network | IPv6Network:
    if isinstance(impl, _ipaddress.IPv4Network):
        return IPv4Network._from_impl(impl)
    return IPv6Network._from_impl(impl)


def _wrap_interface(impl: Any) -> IPv4Interface | IPv6Interface:
    if isinstance(impl, _ipaddress.IPv4Interface):
        return IPv4Interface._from_impl(impl)
    return IPv6Interface._from_impl(impl)


class _AddressBase(_ImplWrapperMixin, _ValueEqMixin, Object):
    """Shared scaffolding for `IPv4Address` / `IPv6Address` wrappers."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    _impl: Any

    @property
    def compressed(self) -> Str:
        return Str(self._impl.compressed)

    @property
    def exploded(self) -> Str:
        return Str(self._impl.exploded)

    @property
    def packed(self) -> Bytes:
        return Bytes(self._impl.packed)

    @property
    def reverse_pointer(self) -> Str:
        return Str(self._impl.reverse_pointer)

    @property
    def is_private(self) -> Boolean:
        return to_boolean(self._impl.is_private)

    @property
    def is_global(self) -> Boolean:
        return to_boolean(self._impl.is_global)

    @property
    def is_multicast(self) -> Boolean:
        return to_boolean(self._impl.is_multicast)

    @property
    def is_unspecified(self) -> Boolean:
        return to_boolean(self._impl.is_unspecified)

    @property
    def is_reserved(self) -> Boolean:
        return to_boolean(self._impl.is_reserved)

    @property
    def is_loopback(self) -> Boolean:
        return to_boolean(self._impl.is_loopback)

    @property
    def is_link_local(self) -> Boolean:
        return to_boolean(self._impl.is_link_local)

    @property
    def version(self) -> Int:
        return Int(self._impl.version)

    @property
    def max_prefixlen(self) -> Int:
        return Int(self._impl.max_prefixlen)

    def __int__(self) -> int:
        return int(self._impl)

    def __add__(self, other: Int) -> _AddressBase:
        return _wrap_address(self._impl + other._value)

    def __sub__(self, other: Int) -> _AddressBase:
        return _wrap_address(self._impl - other._value)

    def __lt__(self, other: _AddressBase) -> Boolean:
        return to_boolean(self._impl < other._impl)

    def __le__(self, other: _AddressBase) -> Boolean:
        return to_boolean(self._impl <= other._impl)

    def __gt__(self, other: _AddressBase) -> Boolean:
        return to_boolean(self._impl > other._impl)

    def __ge__(self, other: _AddressBase) -> Boolean:
        return to_boolean(self._impl >= other._impl)

    def __hash__(self) -> int:
        return hash(self._impl)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class IPv4Address(_AddressBase):
    """Wraps Python's `ipaddress.IPv4Address`."""

    def __init__(self, address: Str | Int | Bytes | IPv4Address) -> None:
        if isinstance(address, IPv4Address):
            self._impl = address._impl
        else:
            self._impl = _ipaddress.IPv4Address(_addr_arg(address))


class IPv6Address(_AddressBase):
    """Wraps Python's `ipaddress.IPv6Address`."""

    def __init__(self, address: Str | Int | Bytes | IPv6Address) -> None:
        if isinstance(address, IPv6Address):
            self._impl = address._impl
        else:
            self._impl = _ipaddress.IPv6Address(_addr_arg(address))


class _NetworkBase(_ImplWrapperMixin, _ValueEqMixin, Object):
    """Shared scaffolding for `IPv4Network` / `IPv6Network` wrappers."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    _impl: Any

    @property
    def network_address(self) -> _AddressBase:
        return _wrap_address(self._impl.network_address)

    @property
    def broadcast_address(self) -> _AddressBase:
        return _wrap_address(self._impl.broadcast_address)

    @property
    def hostmask(self) -> _AddressBase:
        return _wrap_address(self._impl.hostmask)

    @property
    def netmask(self) -> _AddressBase:
        return _wrap_address(self._impl.netmask)

    @property
    def prefixlen(self) -> Int:
        return Int(self._impl.prefixlen)

    @property
    def with_prefixlen(self) -> Str:
        return Str(self._impl.with_prefixlen)

    @property
    def with_netmask(self) -> Str:
        return Str(self._impl.with_netmask)

    @property
    def with_hostmask(self) -> Str:
        return Str(self._impl.with_hostmask)

    @property
    def num_addresses(self) -> Int:
        return Int(self._impl.num_addresses)

    @property
    def version(self) -> Int:
        return Int(self._impl.version)

    @property
    def is_private(self) -> Boolean:
        return to_boolean(self._impl.is_private)

    @property
    def is_global(self) -> Boolean:
        return to_boolean(self._impl.is_global)

    @property
    def is_multicast(self) -> Boolean:
        return to_boolean(self._impl.is_multicast)

    def hosts(self) -> List:
        return List(*(_wrap_address(h) for h in self._impl.hosts()))

    def subnets(
        self,
        prefixlen_diff: Int | None = None,
        new_prefix: Int | None = None,
    ) -> List:
        kwargs: dict[str, int] = {}
        kwargs.update(
            _kwargs_from(prefixlen_diff=prefixlen_diff, new_prefix=new_prefix)
        )
        return List(*(_wrap_network(s) for s in self._impl.subnets(**kwargs)))

    def supernet(
        self,
        prefixlen_diff: Int | None = None,
        new_prefix: Int | None = None,
    ) -> _NetworkBase:
        kwargs: dict[str, int] = {}
        kwargs.update(
            _kwargs_from(prefixlen_diff=prefixlen_diff, new_prefix=new_prefix)
        )
        return _wrap_network(self._impl.supernet(**kwargs))

    def overlaps(self, other: _NetworkBase) -> Boolean:
        return to_boolean(self._impl.overlaps(other._impl))

    def compare_networks(self, other: _NetworkBase) -> Int:
        return Int(self._impl.compare_networks(other._impl))

    def address_exclude(self, network: _NetworkBase) -> List:
        return List(
            *(_wrap_network(n) for n in self._impl.address_exclude(network._impl))
        )

    def subnet_of(self, other: _NetworkBase) -> Boolean:
        return to_boolean(self._impl.subnet_of(other._impl))

    def supernet_of(self, other: _NetworkBase) -> Boolean:
        return to_boolean(self._impl.supernet_of(other._impl))

    def __iter__(self) -> Iterator[_AddressBase]:
        for addr in self._impl:
            yield _wrap_address(addr)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, _AddressBase):
            return item._impl in self._impl
        return item in self._impl

    def __hash__(self) -> int:
        return hash(self._impl)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class IPv4Network(_NetworkBase):
    """Wraps Python's `ipaddress.IPv4Network`."""

    def __init__(
        self,
        address: Str | Int | Bytes | IPv4Address | IPv4Network,
        strict: Boolean | None = None,
    ) -> None:
        if isinstance(address, IPv4Network):
            self._impl = address._impl
        else:
            self._impl = _ipaddress.IPv4Network(
                _addr_arg(address), strict=_b(strict, True)
            )


class IPv6Network(_NetworkBase):
    """Wraps Python's `ipaddress.IPv6Network`."""

    def __init__(
        self,
        address: Str | Int | Bytes | IPv6Address | IPv6Network,
        strict: Boolean | None = None,
    ) -> None:
        if isinstance(address, IPv6Network):
            self._impl = address._impl
        else:
            self._impl = _ipaddress.IPv6Network(
                _addr_arg(address), strict=_b(strict, True)
            )


class _InterfaceBase(_ImplWrapperMixin, _ValueEqMixin, Object):
    """Shared scaffolding for `IPv4Interface` / `IPv6Interface` wrappers."""

    __slots__ = ("_impl",)
    _eq_attr: ClassVar[str] = "_impl"

    _impl: Any

    @property
    def ip(self) -> _AddressBase:
        return _wrap_address(self._impl.ip)

    @property
    def network(self) -> _NetworkBase:
        return _wrap_network(self._impl.network)

    @property
    def with_prefixlen(self) -> Str:
        return Str(self._impl.with_prefixlen)

    @property
    def with_netmask(self) -> Str:
        return Str(self._impl.with_netmask)

    @property
    def with_hostmask(self) -> Str:
        return Str(self._impl.with_hostmask)

    @property
    def version(self) -> Int:
        return Int(self._impl.version)

    def __hash__(self) -> int:
        return hash(self._impl)

    def __str__(self) -> str:
        return str(self._impl)

    __repr__ = __str__


class IPv4Interface(_InterfaceBase):
    """Wraps Python's `ipaddress.IPv4Interface`."""

    def __init__(
        self, address: Str | Int | Bytes | IPv4Address | IPv4Interface
    ) -> None:
        if isinstance(address, IPv4Interface):
            self._impl = address._impl
        else:
            self._impl = _ipaddress.IPv4Interface(_addr_arg(address))


class IPv6Interface(_InterfaceBase):
    """Wraps Python's `ipaddress.IPv6Interface`."""

    def __init__(
        self, address: Str | Int | Bytes | IPv6Address | IPv6Interface
    ) -> None:
        if isinstance(address, IPv6Interface):
            self._impl = address._impl
        else:
            self._impl = _ipaddress.IPv6Interface(_addr_arg(address))


class Ipaddress:
    """Namespace mirroring Python's `ipaddress` module.

    Factory functions (`ip_address` / `ip_network` / `ip_interface`)
    return whichever IPv4/IPv6 wrapper matches the input;
    `summarize_address_range` and `collapse_addresses` operate on
    sequences. `AddressValueError` and `NetmaskValueError` are
    exposed for `Try.except_`.
    """

    IPv4Address: ClassVar[type[IPv4Address]] = IPv4Address
    IPv6Address: ClassVar[type[IPv6Address]] = IPv6Address
    IPv4Network: ClassVar[type[IPv4Network]] = IPv4Network
    IPv6Network: ClassVar[type[IPv6Network]] = IPv6Network
    IPv4Interface: ClassVar[type[IPv4Interface]] = IPv4Interface
    IPv6Interface: ClassVar[type[IPv6Interface]] = IPv6Interface

    AddressValueError: ClassVar[type[Exception]] = _ipaddress.AddressValueError
    NetmaskValueError: ClassVar[type[Exception]] = _ipaddress.NetmaskValueError

    @staticmethod
    def ip_address(
        address: Str | Int | Bytes,
    ) -> IPv4Address | IPv6Address:
        return _wrap_address(_ipaddress.ip_address(_addr_arg(address)))

    @staticmethod
    def ip_network(
        address: Str | Int | Bytes,
        strict: Boolean | None = None,
    ) -> IPv4Network | IPv6Network:
        return _wrap_network(
            _ipaddress.ip_network(_addr_arg(address), strict=_b(strict, True))
        )

    @staticmethod
    def ip_interface(
        address: Str | Int | Bytes,
    ) -> IPv4Interface | IPv6Interface:
        return _wrap_interface(_ipaddress.ip_interface(_addr_arg(address)))

    @staticmethod
    def summarize_address_range(first: _AddressBase, last: _AddressBase) -> List:
        return List(
            *(
                _wrap_network(n)
                for n in _ipaddress.summarize_address_range(first._impl, last._impl)
            )
        )

    @staticmethod
    def collapse_addresses(addresses: List) -> List:
        unwrapped: list[Any] = []
        for a in addresses:
            if isinstance(a, _NetworkBase | _AddressBase):
                unwrapped.append(a._impl)
            else:
                raise TypeError(
                    f"collapse_addresses entries must be addresses or networks, got {type(a).__name__}"
                )
        return List(
            *(_wrap_network(n) for n in _ipaddress.collapse_addresses(unwrapped))
        )

    @staticmethod
    def get_mixed_type_key(obj: Any) -> Tuple | NoneClass:
        impl = obj._impl if hasattr(obj, "_impl") else obj
        result = _ipaddress.get_mixed_type_key(impl)
        if result is NotImplemented:
            return none
        version = Int(result[0])
        wrapped = [_wrap_address(item) for item in result[1:]]
        return Tuple(version, *wrapped)
