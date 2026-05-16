import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import false, true
from poop.types.bytes import Bytes
from poop.types.int import Int
from poop.types.ipaddress import (
    Ipaddress,
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from poop.types.list import List
from poop.types.string import Str

# --- IPv4Address ---


def test_ipv4_from_str() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    assert a.compressed == Str("192.0.2.1")
    assert a.version == Int(4)
    assert a.max_prefixlen == Int(32)


def test_ipv4_from_int() -> None:
    assert IPv4Address(Int(0xC0000201)).compressed == Str("192.0.2.1")


def test_ipv4_from_bytes() -> None:
    assert IPv4Address(Bytes(b"\xc0\x00\x02\x01")).compressed == Str("192.0.2.1")


def test_ipv4_exploded_and_packed() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    assert a.exploded == Str("192.0.2.1")
    assert a.packed == Bytes(b"\xc0\x00\x02\x01")


def test_ipv4_predicates() -> None:
    assert IPv4Address(Str("127.0.0.1")).is_loopback is true
    assert IPv4Address(Str("224.0.0.1")).is_multicast is true
    assert IPv4Address(Str("192.0.2.1")).is_global is false
    assert IPv4Address(Str("10.0.0.1")).is_private is true


def test_ipv4_arithmetic() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    b = a + Int(1)
    assert isinstance(b, IPv4Address)
    assert b.compressed == Str("192.0.2.2")
    c = b - Int(1)
    assert c == a


def test_ipv4_comparison() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    b = IPv4Address(Str("192.0.2.5"))
    assert (a < b) is true
    assert (a <= b) is true
    assert (b > a) is true
    assert (b >= a) is true


def test_ipv4_reverse_pointer() -> None:
    assert IPv4Address(Str("192.0.2.1")).reverse_pointer == Str(
        "1.2.0.192.in-addr.arpa"
    )


def test_ipv4_invalid_raises() -> None:
    with pytest.raises(Ipaddress.AddressValueError):
        IPv4Address(Str("not.an.ip"))


# --- IPv6Address ---


def test_ipv6_basic() -> None:
    a = IPv6Address(Str("2001:db8::1"))
    assert a.version == Int(6)
    assert a.max_prefixlen == Int(128)
    assert a.compressed == Str("2001:db8::1")


def test_ipv6_predicates() -> None:
    assert IPv6Address(Str("::1")).is_loopback is true
    assert IPv6Address(Str("ff00::1")).is_multicast is true


# --- IPv4Network ---


def test_ipv4_network_basic() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    assert isinstance(n.network_address, IPv4Address)
    assert n.network_address == IPv4Address(Str("192.0.2.0"))
    assert n.broadcast_address == IPv4Address(Str("192.0.2.255"))
    assert n.prefixlen == Int(24)
    assert n.num_addresses == Int(256)


def test_ipv4_network_iteration() -> None:
    n = IPv4Network(Str("192.0.2.0/30"))
    addrs = [a for a in n]
    assert len(addrs) == 4
    assert all(isinstance(a, IPv4Address) for a in addrs)


def test_ipv4_network_hosts() -> None:
    n = IPv4Network(Str("192.0.2.0/30"))
    hosts = n.hosts()
    assert isinstance(hosts, List)
    assert hosts.len() == Int(2)


def test_ipv4_network_subnets() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    subs = n.subnets()
    assert isinstance(subs, List)
    assert subs.len() == Int(2)
    assert all(isinstance(s, IPv4Network) for s in subs)


def test_ipv4_network_subnets_with_new_prefix() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    subs = n.subnets(new_prefix=Int(26))
    assert subs.len() == Int(4)


def test_ipv4_network_supernet() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    sup = n.supernet()
    assert isinstance(sup, IPv4Network)
    assert sup.prefixlen == Int(23)


def test_ipv4_network_supernet_with_new_prefix() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    sup = n.supernet(new_prefix=Int(16))
    assert sup.prefixlen == Int(16)


def test_ipv4_network_overlaps() -> None:
    a = IPv4Network(Str("192.0.2.0/24"))
    b = IPv4Network(Str("192.0.2.128/25"))
    c = IPv4Network(Str("198.51.100.0/24"))
    assert a.overlaps(b) is true
    assert a.overlaps(c) is false


def test_ipv4_network_subnet_of_and_supernet_of() -> None:
    big = IPv4Network(Str("192.0.2.0/24"))
    small = IPv4Network(Str("192.0.2.0/26"))
    assert small.subnet_of(big) is true
    assert big.supernet_of(small) is true


def test_ipv4_network_address_exclude() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    excluded = IPv4Network(Str("192.0.2.0/25"))
    result = n.address_exclude(excluded)
    assert isinstance(result, List)
    assert result.len() == Int(1)


def test_ipv4_network_compare_networks() -> None:
    a = IPv4Network(Str("192.0.2.0/24"))
    b = IPv4Network(Str("192.0.3.0/24"))
    assert a.compare_networks(b) == Int(-1)


def test_ipv4_network_contains() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    assert IPv4Address(Str("192.0.2.5")) in n
    assert IPv4Address(Str("203.0.113.1")) not in n


def test_ipv4_network_with_strings() -> None:
    n = IPv4Network(Str("192.0.2.0/24"))
    assert n.with_prefixlen == Str("192.0.2.0/24")
    assert isinstance(n.with_netmask, Str)
    assert isinstance(n.with_hostmask, Str)


def test_ipv4_network_strict_false_allows_host_bits() -> None:
    n = IPv4Network(Str("192.0.2.1/24"), strict=false)
    assert n.network_address == IPv4Address(Str("192.0.2.0"))


def test_ipv4_network_predicates() -> None:
    assert IPv4Network(Str("10.0.0.0/8")).is_private is true
    assert IPv4Network(Str("224.0.0.0/4")).is_multicast is true


def test_ipv4_network_version() -> None:
    assert IPv4Network(Str("0.0.0.0/0")).version == Int(4)


# --- IPv6Network ---


def test_ipv6_network_basic() -> None:
    n = IPv6Network(Str("2001:db8::/32"))
    assert isinstance(n.network_address, IPv6Address)
    assert n.version == Int(6)
    assert n.prefixlen == Int(32)


# --- Interfaces ---


def test_ipv4_interface() -> None:
    i = IPv4Interface(Str("192.0.2.1/24"))
    assert i.ip == IPv4Address(Str("192.0.2.1"))
    assert i.network == IPv4Network(Str("192.0.2.0/24"))
    assert i.version == Int(4)
    assert i.with_prefixlen == Str("192.0.2.1/24")


def test_ipv6_interface() -> None:
    i = IPv6Interface(Str("2001:db8::1/64"))
    assert i.version == Int(6)
    assert isinstance(i.network, IPv6Network)


# --- Factories ---


def test_ip_address_factory_ipv4() -> None:
    a = Ipaddress.ip_address(Str("192.0.2.1"))
    assert isinstance(a, IPv4Address)


def test_ip_address_factory_ipv6() -> None:
    a = Ipaddress.ip_address(Str("2001:db8::1"))
    assert isinstance(a, IPv6Address)


def test_ip_network_factory() -> None:
    assert isinstance(Ipaddress.ip_network(Str("192.0.2.0/24")), IPv4Network)
    assert isinstance(Ipaddress.ip_network(Str("2001:db8::/32")), IPv6Network)


def test_ip_interface_factory() -> None:
    assert isinstance(Ipaddress.ip_interface(Str("192.0.2.1/24")), IPv4Interface)
    assert isinstance(Ipaddress.ip_interface(Str("2001:db8::1/64")), IPv6Interface)


def test_summarize_address_range() -> None:
    first = IPv4Address(Str("192.0.2.0"))
    last = IPv4Address(Str("192.0.2.255"))
    result = Ipaddress.summarize_address_range(first, last)
    assert isinstance(result, List)
    assert result.len() == Int(1)
    assert result.at(Int(0)) == IPv4Network(Str("192.0.2.0/24"))


def test_collapse_addresses() -> None:
    addresses = List(
        IPv4Network(Str("192.0.2.0/25")),
        IPv4Network(Str("192.0.2.128/25")),
    )
    result = Ipaddress.collapse_addresses(addresses)
    assert isinstance(result, List)
    assert result.len() == Int(1)
    assert result.at(Int(0)) == IPv4Network(Str("192.0.2.0/24"))


def test_collapse_addresses_rejects_non_addresses() -> None:
    with pytest.raises(TypeError):
        Ipaddress.collapse_addresses(List(Int(1)))


def test_get_mixed_type_key() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    result = Ipaddress.get_mixed_type_key(a)
    assert result is not None


# --- Errors ---


def test_netmask_value_error_raises() -> None:
    with pytest.raises(Ipaddress.NetmaskValueError):
        IPv4Network(Str("192.0.2.0/33"))


# --- Interpreter integration ---


def test_ip_address_via_interpreter() -> None:
    Interpreter().run_source('ipaddress.ip_address("192.0.2.1").compressed.print()')


def test_ipv4_network_via_interpreter() -> None:
    Interpreter().run_source('IPv4Network("192.0.2.0/24").prefixlen.print()')


def test_ipv6_address_via_interpreter() -> None:
    Interpreter().run_source('IPv6Address("2001:db8::1").compressed.print()')


# --- Extra coverage ---


def test_ipv4_address_unspecified_and_reserved() -> None:
    assert IPv4Address(Str("0.0.0.0")).is_unspecified is true
    assert IPv4Address(Str("240.0.0.1")).is_reserved is true


def test_ipv4_address_link_local() -> None:
    assert IPv4Address(Str("169.254.0.1")).is_link_local is true


def test_ipv4_address_int_conversion() -> None:
    assert int(IPv4Address(Str("0.0.0.1"))) == 1


def test_ipv4_address_construction_from_poop_address() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    b = IPv4Address(a)
    assert a == b


def test_ipv6_address_construction_from_poop_address() -> None:
    a = IPv6Address(Str("::1"))
    b = IPv6Address(a)
    assert a == b


def test_ipv4_network_construction_from_poop_network() -> None:
    a = IPv4Network(Str("192.0.2.0/24"))
    b = IPv4Network(a)
    assert a == b


def test_ipv6_network_construction_from_poop_network() -> None:
    a = IPv6Network(Str("2001:db8::/32"))
    b = IPv6Network(a)
    assert a == b


def test_ipv4_interface_construction_from_poop_interface() -> None:
    a = IPv4Interface(Str("192.0.2.1/24"))
    b = IPv4Interface(a)
    assert isinstance(b, IPv4Interface)


def test_ipv6_interface_construction_from_poop_interface() -> None:
    a = IPv6Interface(Str("2001:db8::1/64"))
    b = IPv6Interface(a)
    assert isinstance(b, IPv6Interface)


def test_ipv4_interface_with_netmask_hostmask() -> None:
    i = IPv4Interface(Str("192.0.2.1/24"))
    assert isinstance(i.with_netmask, Str)
    assert isinstance(i.with_hostmask, Str)


def test_address_compare_le_ge() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    b = IPv4Address(Str("192.0.2.1"))
    assert (a <= b) is true
    assert (a >= b) is true


def test_address_hash_consistent() -> None:
    a = IPv4Address(Str("192.0.2.1"))
    b = IPv4Address(Str("192.0.2.1"))
    assert hash(a) == hash(b)


def test_ipv6_address_int_conversion() -> None:
    assert int(IPv6Address(Str("::1"))) == 1


def test_ipv4_network_predicates_global_multicast() -> None:
    assert IPv4Network(Str("224.0.0.0/4")).is_multicast is true
    assert IPv4Network(Str("203.0.113.0/24")).is_global is false


def test_network_contains_raw_int() -> None:
    n = IPv4Network(Str("192.0.2.0/30"))
    assert n.network_address._impl in n
