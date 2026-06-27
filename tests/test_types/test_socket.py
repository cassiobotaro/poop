from typing import cast

import pytest

from poop.interpreter import Interpreter
from poop.types.boolean import Boolean
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.none import none
from poop.types.socket import Socket, SocketNamespace
from poop.types.string import Str
from poop.types.tuple import Tuple


def test_socket_constructs_default() -> None:
    s = Socket()
    try:
        assert isinstance(s, Socket)
    finally:
        s.close()


def test_socket_constructs_with_family_and_type() -> None:
    s = Socket(SocketNamespace.AF_INET, SocketNamespace.SOCK_DGRAM)
    try:
        assert isinstance(s, Socket)
    finally:
        s.close()


def test_socket_constructs_with_poop_none_args() -> None:
    # POOP's `none` (NoneClass) must be accepted like an omitted argument,
    # not crash with AttributeError on `._value`.
    s = Socket(none, none, none)
    try:
        assert isinstance(s, Socket)
    finally:
        s.close()


def test_socket_fileno_returns_int() -> None:
    s = Socket()
    try:
        assert isinstance(s.fileno(), Int)
    finally:
        s.close()


def test_socket_settimeout_and_gettimeout() -> None:
    s = Socket()
    try:
        s.settimeout(Float(1.5))
        assert s.gettimeout() == Float(1.5)
        s.settimeout(none)
        assert s.gettimeout() is none
    finally:
        s.close()


def test_socket_setblocking() -> None:
    s = Socket()
    try:
        from poop.types.boolean import false

        assert s.setblocking(false) is none
    finally:
        s.close()


def test_socket_context_manager() -> None:
    with Socket() as s:
        assert isinstance(s.fileno(), Int)


def test_socket_bind_and_getsockname() -> None:
    s = Socket()
    try:
        s.bind(Tuple(Str("127.0.0.1"), Int(0)))
        name = s.getsockname()
        assert isinstance(name, Tuple)
    finally:
        s.close()


def test_socket_listen_and_close() -> None:
    s = Socket()
    try:
        s.bind(Tuple(Str("127.0.0.1"), Int(0)))
        assert s.listen() is none
    finally:
        assert s.close() is none


def test_socket_listen_with_backlog() -> None:
    s = Socket()
    try:
        s.bind(Tuple(Str("127.0.0.1"), Int(0)))
        assert s.listen(Int(5)) is none
    finally:
        s.close()


def test_socket_accept_and_connect() -> None:
    server = Socket()
    try:
        server.bind(Tuple(Str("127.0.0.1"), Int(0)))
        server.listen(Int(1))
        port = server.getsockname().at(Int(1))

        client = Socket()
        try:
            client.connect(Tuple(Str("127.0.0.1"), port))
            pair = server.accept()
            conn = pair.at(Int(0))
            assert isinstance(conn, Socket)
            conn.close()
        finally:
            client.close()
    finally:
        server.close()


def test_socket_send_recv() -> None:
    server = Socket()
    try:
        server.bind(Tuple(Str("127.0.0.1"), Int(0)))
        server.listen(Int(1))
        port = server.getsockname().at(Int(1))
        assert isinstance(port, Int)

        client = Socket()
        try:
            client.connect(Tuple(Str("127.0.0.1"), port))
            pair = server.accept()
            conn = pair.at(Int(0))
            assert isinstance(conn, Socket)
            try:
                assert isinstance(client.send(Bytes(b"hi")), Int)
                data = conn.recv(Int(2))
                assert data == Bytes(b"hi")
            finally:
                conn.close()
        finally:
            client.close()
    finally:
        server.close()


def test_socket_sendall_returns_none() -> None:
    server = Socket()
    try:
        server.bind(Tuple(Str("127.0.0.1"), Int(0)))
        server.listen(Int(1))
        port = server.getsockname().at(Int(1))
        assert isinstance(port, Int)

        client = Socket()
        try:
            client.connect(Tuple(Str("127.0.0.1"), port))
            pair = server.accept()
            conn = pair.at(Int(0))
            assert isinstance(conn, Socket)
            try:
                assert client.sendall(Bytes(b"xx")) is none
                assert conn.recv(Int(2)) == Bytes(b"xx")
            finally:
                conn.close()
        finally:
            client.close()
    finally:
        server.close()


def test_socket_connect_ex() -> None:
    # Connect to a port that almost certainly nothing is listening on.
    client = Socket()
    try:
        result = client.connect_ex(Tuple(Str("127.0.0.1"), Int(1)))
        assert isinstance(result, Int)
    finally:
        client.close()


def test_socket_setsockopt_and_getsockopt() -> None:
    s = Socket()
    try:
        s.setsockopt(SocketNamespace.SOL_SOCKET, SocketNamespace.SO_REUSEADDR, Int(1))
        value = s.getsockopt(SocketNamespace.SOL_SOCKET, SocketNamespace.SO_REUSEADDR)
        assert isinstance(value, Int)
    finally:
        s.close()


def test_socket_shutdown() -> None:
    server = Socket()
    try:
        server.bind(Tuple(Str("127.0.0.1"), Int(0)))
        server.listen(Int(1))
        port = server.getsockname().at(Int(1))

        client = Socket()
        try:
            client.connect(Tuple(Str("127.0.0.1"), port))
            assert client.shutdown(SocketNamespace.SHUT_WR) is none
        finally:
            client.close()
    finally:
        server.close()


def test_udp_sendto_and_recvfrom() -> None:
    server = Socket(SocketNamespace.AF_INET, SocketNamespace.SOCK_DGRAM)
    try:
        server.bind(Tuple(Str("127.0.0.1"), Int(0)))
        port = server.getsockname().at(Int(1))

        client = Socket(SocketNamespace.AF_INET, SocketNamespace.SOCK_DGRAM)
        try:
            assert isinstance(
                client.sendto(Bytes(b"udp"), Tuple(Str("127.0.0.1"), port)), Int
            )
            pair = server.recvfrom(Int(8))
            assert isinstance(pair, Tuple)
            data = pair.at(Int(0))
            assert data == Bytes(b"udp")
        finally:
            client.close()
    finally:
        server.close()


# --- Module-level helpers ---


def test_gethostname_returns_str() -> None:
    assert isinstance(SocketNamespace.gethostname(), Str)


def test_gethostbyname_localhost() -> None:
    result = SocketNamespace.gethostbyname(Str("localhost"))
    assert isinstance(result, Str)


def test_gethostbyname_ex() -> None:
    result = SocketNamespace.gethostbyname_ex(Str("localhost"))
    assert isinstance(result, Tuple)
    assert result.len() == Int(3)


def test_getfqdn() -> None:
    assert isinstance(SocketNamespace.getfqdn(), Str)


def test_getfqdn_with_name() -> None:
    assert isinstance(SocketNamespace.getfqdn(Str("localhost")), Str)


def test_getfqdn_with_poop_none() -> None:
    # Passing POOP's `none` must behave like an omitted argument.
    assert isinstance(SocketNamespace.getfqdn(none), Str)


def test_has_dualstack_ipv6_returns_boolean() -> None:
    assert isinstance(SocketNamespace.has_dualstack_ipv6(), Boolean)


def test_getservbyname() -> None:
    try:
        result = SocketNamespace.getservbyname(Str("http"))
        assert isinstance(result, Int)
    except OSError:
        pytest.skip("http service not registered on this host")


def test_getservbyname_with_protocol() -> None:
    try:
        result = SocketNamespace.getservbyname(Str("http"), Str("tcp"))
        assert isinstance(result, Int)
    except OSError:
        pytest.skip("http service not registered on this host")


def test_getservbyname_with_poop_none_protocol() -> None:
    # POOP's `none` for the optional protocol must not crash on `._value`.
    try:
        result = SocketNamespace.getservbyname(Str("http"), none)
        assert isinstance(result, Int)
    except OSError:
        pytest.skip("http service not registered on this host")


def test_getservbyport() -> None:
    try:
        result = SocketNamespace.getservbyport(Int(80))
        assert isinstance(result, Str)
    except OSError:
        pytest.skip("port 80 not registered on this host")


def test_getservbyport_with_protocol() -> None:
    try:
        result = SocketNamespace.getservbyport(Int(80), Str("tcp"))
        assert isinstance(result, Str)
    except OSError:
        pytest.skip("port 80 not registered on this host")


def test_htons_ntohs_round_trip() -> None:
    assert SocketNamespace.ntohs(SocketNamespace.htons(Int(123))) == Int(123)


def test_htonl_ntohl_round_trip() -> None:
    assert SocketNamespace.ntohl(SocketNamespace.htonl(Int(123456))) == Int(123456)


def test_inet_aton_ntoa_round_trip() -> None:
    packed = SocketNamespace.inet_aton(Str("127.0.0.1"))
    assert isinstance(packed, Bytes)
    assert SocketNamespace.inet_ntoa(packed) == Str("127.0.0.1")


def test_inet_pton_ntop_round_trip() -> None:
    packed = SocketNamespace.inet_pton(SocketNamespace.AF_INET, Str("127.0.0.1"))
    assert isinstance(packed, Bytes)
    assert SocketNamespace.inet_ntop(SocketNamespace.AF_INET, packed) == Str(
        "127.0.0.1"
    )


def test_create_connection() -> None:
    # Use a localhost listener.
    server = Socket()
    try:
        server.bind(Tuple(Str("127.0.0.1"), Int(0)))
        server.listen(Int(1))
        port = server.getsockname().at(Int(1))
        client = SocketNamespace.create_connection(Tuple(Str("127.0.0.1"), port))
        try:
            assert isinstance(client, Socket)
        finally:
            client.close()
    finally:
        server.close()


def test_create_connection_with_timeout() -> None:
    server = Socket()
    try:
        server.bind(Tuple(Str("127.0.0.1"), Int(0)))
        server.listen(Int(1))
        port = server.getsockname().at(Int(1))
        client = SocketNamespace.create_connection(
            Tuple(Str("127.0.0.1"), port), Float(1.0)
        )
        try:
            assert isinstance(client, Socket)
        finally:
            client.close()
    finally:
        server.close()


def test_create_server() -> None:
    server = SocketNamespace.create_server(Tuple(Str("127.0.0.1"), Int(0)))
    try:
        assert isinstance(server, Socket)
    finally:
        server.close()


def test_create_server_with_family() -> None:
    server = SocketNamespace.create_server(
        Tuple(Str("127.0.0.1"), Int(0)), family=SocketNamespace.AF_INET
    )
    try:
        assert isinstance(server, Socket)
    finally:
        server.close()


# --- Constants ---


def test_constants_are_ints() -> None:
    for attr in (
        "AF_INET",
        "AF_INET6",
        "AF_UNSPEC",
        "SOCK_STREAM",
        "SOCK_DGRAM",
        "SOCK_RAW",
        "SOL_SOCKET",
        "SO_REUSEADDR",
        "SO_KEEPALIVE",
        "SO_BROADCAST",
        "SHUT_RD",
        "SHUT_WR",
        "SHUT_RDWR",
    ):
        assert isinstance(getattr(SocketNamespace, attr), Int)


def test_socket_class_ref() -> None:
    assert SocketNamespace.Socket is Socket


# --- Interpreter integration ---


def test_socket_via_interpreter() -> None:
    Interpreter().run_source("s = Socket()\ns.fileno().print()\ns.close()")


# --- getaddrinfo / getnameinfo / if_* ---


def test_getaddrinfo_returns_list_of_tuples() -> None:
    from poop.types.list import List

    out = SocketNamespace.getaddrinfo(Str("localhost"), Int(80))
    assert isinstance(out, List)
    first = out.at(Int(0))
    assert isinstance(first, Tuple)
    family = first.at(Int(0))
    assert isinstance(family, Int)


def test_if_nameindex_returns_list_of_tuples() -> None:
    from poop.types.list import List

    out = SocketNamespace.if_nameindex()
    assert isinstance(out, List)
    if out.len()._value > 0:
        first = out.at(Int(0))
        assert isinstance(first, Tuple)
        assert isinstance(first.at(Int(0)), Int)
        assert isinstance(first.at(Int(1)), Str)


def test_if_nametoindex_round_trip() -> None:
    out = SocketNamespace.if_nameindex()
    if out.len()._value == 0:
        pytest.skip("no network interfaces present")
    first = cast(Tuple, out.at(Int(0)))
    name = cast(Str, first.at(Int(1)))
    idx = SocketNamespace.if_nametoindex(name)
    assert isinstance(idx, Int)
    assert SocketNamespace.if_indextoname(idx) == name


def test_SocketType_is_underlying_class() -> None:
    import socket as _stdlib_socket

    assert SocketNamespace.SocketType is _stdlib_socket.socket
