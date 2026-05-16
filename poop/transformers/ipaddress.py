from poop.types.ipaddress import (
    Ipaddress,
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)

NAMESPACE: dict[str, object] = {
    "ipaddress": Ipaddress,
    "IPv4Address": IPv4Address,
    "IPv6Address": IPv6Address,
    "IPv4Network": IPv4Network,
    "IPv6Network": IPv6Network,
    "IPv4Interface": IPv4Interface,
    "IPv6Interface": IPv6Interface,
}
