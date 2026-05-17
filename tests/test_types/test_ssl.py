from poop.interpreter import Interpreter
from poop.types.boolean import Boolean
from poop.types.int import Int
from poop.types.none import none
from poop.types.ssl import SSL, SSLContext


def test_create_default_context_no_args() -> None:
    ctx = SSL.create_default_context()
    assert isinstance(ctx, SSLContext)


def test_ssl_context_constructs() -> None:
    ctx = SSLContext()
    assert isinstance(ctx, SSLContext)


def test_verify_mode_round_trip() -> None:
    ctx = SSL.create_default_context()
    assert isinstance(ctx.verify_mode, Int)
    # check_hostname=True requires verify_mode != CERT_NONE — disable it first.
    from poop.types.boolean import false

    ctx.check_hostname = false
    ctx.verify_mode = SSL.CERT_NONE
    assert ctx.verify_mode == SSL.CERT_NONE


def test_check_hostname_round_trip() -> None:
    ctx = SSL.create_default_context()
    assert isinstance(ctx.check_hostname, Boolean)
    # Disable check_hostname first (the default context has it enabled);
    # then verify_mode can drop to CERT_NONE.
    from poop.types.boolean import false

    ctx.check_hostname = false
    assert ctx.check_hostname is false


def test_get_ciphers_returns_object() -> None:
    ctx = SSL.create_default_context()
    ciphers = ctx.get_ciphers()
    assert isinstance(ciphers, list)


def test_set_ciphers_returns_none() -> None:
    ctx = SSL.create_default_context()
    from poop.types.string import Str

    # 'DEFAULT' is a reliable cipher spec across OpenSSL versions.
    assert ctx.set_ciphers(Str("DEFAULT")) is none


def test_load_default_certs_returns_none() -> None:
    ctx = SSL.create_default_context()
    assert ctx.load_default_certs() is none


def test_constants_are_ints() -> None:
    assert isinstance(SSL.PROTOCOL_TLS_CLIENT, Int)
    assert isinstance(SSL.PROTOCOL_TLS_SERVER, Int)
    assert isinstance(SSL.CERT_NONE, Int)
    assert isinstance(SSL.CERT_OPTIONAL, Int)
    assert isinstance(SSL.CERT_REQUIRED, Int)


def test_error_classes_are_exceptions() -> None:
    assert issubclass(SSL.SSLError, Exception)
    assert issubclass(SSL.SSLZeroReturnError, Exception)
    assert issubclass(SSL.SSLWantReadError, Exception)
    assert issubclass(SSL.SSLWantWriteError, Exception)
    assert issubclass(SSL.SSLSyscallError, Exception)
    assert issubclass(SSL.SSLEOFError, Exception)
    assert issubclass(SSL.SSLCertVerificationError, Exception)


def test_ssl_class_ref() -> None:
    assert SSL.SSLContext is SSLContext


# --- Wrap socket ---


def test_wrap_socket_returns_socket() -> None:
    from poop.types.socket import Socket
    from poop.types.string import Str

    ctx = SSL.create_default_context()
    raw = Socket()
    try:
        wrapped = ctx.wrap_socket(raw, server_hostname=Str("example.com"))
        try:
            from poop.types.socket import Socket as _Socket

            assert isinstance(wrapped, _Socket)
        finally:
            wrapped.close()
    finally:
        # raw is owned by wrapped now; ignore double-close.
        try:
            raw.close()
        except OSError:
            pass


# --- Interpreter integration ---


def test_ssl_constants_via_interpreter() -> None:
    Interpreter().run_source("ssl.CERT_REQUIRED.print()")


# --- load_cert_chain / load_verify_locations error paths ---


def test_load_cert_chain_rejects_missing_file() -> None:
    import pytest

    from poop.types.string import Str

    ctx = SSL.create_default_context()
    with pytest.raises(FileNotFoundError):
        ctx.load_cert_chain(Str("/does/not/exist/poop.pem"))


def test_load_cert_chain_with_path_object() -> None:
    import pytest

    from poop.types.path import Path
    from poop.types.string import Str

    ctx = SSL.create_default_context()
    # Path argument triggers the Path-handling branch in load_cert_chain.
    with pytest.raises(FileNotFoundError):
        ctx.load_cert_chain(Path(Str("/does/not/exist/poop.pem")))


def test_load_cert_chain_with_keyfile_and_password() -> None:
    import pytest

    from poop.types.string import Str

    ctx = SSL.create_default_context()
    with pytest.raises(FileNotFoundError):
        ctx.load_cert_chain(
            Str("/does/not/exist/poop.pem"),
            keyfile=Str("/does/not/exist/key.pem"),
            password=Str("secret"),
        )


def test_load_verify_locations_rejects_missing_cafile() -> None:
    import pytest

    from poop.types.string import Str

    ctx = SSL.create_default_context()
    with pytest.raises(FileNotFoundError):
        ctx.load_verify_locations(cafile=Str("/does/not/exist/poop.pem"))


def test_load_verify_locations_with_path_objects() -> None:
    import pytest

    from poop.types.path import Path
    from poop.types.string import Str

    ctx = SSL.create_default_context()
    with pytest.raises((FileNotFoundError, NotADirectoryError, OSError)):
        ctx.load_verify_locations(
            cafile=Path(Str("/does/not/exist/poop.pem")),
            capath=Path(Str("/does/not/exist/dir")),
        )


def test_load_verify_locations_with_cadata_str() -> None:
    import pytest

    from poop.types.string import Str

    ctx = SSL.create_default_context()
    # Invalid PEM data raises an SSLError from OpenSSL.
    with pytest.raises(Exception):  # noqa: B017
        ctx.load_verify_locations(cadata=Str("not a real PEM cert"))


def test_wrap_socket_server_side_branch() -> None:
    import pytest

    from poop.types.boolean import true
    from poop.types.socket import Socket

    ctx = SSLContext()
    raw = Socket()
    try:
        # Reaches the server_side kwarg-set path before OpenSSL raises for
        # a context without a loaded cert chain.
        with pytest.raises(ValueError):
            ctx.wrap_socket(raw, server_side=true)
    finally:
        try:
            raw.close()
        except OSError:
            pass


# --- Try.except_ integration ---


def test_try_catches_missing_cert_file() -> None:
    from poop.types.string import Str
    from poop.types.try_ import Try

    captured: list[object] = []
    ctx = SSL.create_default_context()
    Try(lambda: ctx.load_cert_chain(Str("/does/not/exist/poop.pem"))).except_(
        FileNotFoundError, lambda e: captured.append(e.kind())
    ).run()
    assert len(captured) == 1


def test_try_catches_invalid_cadata() -> None:
    from poop.types.string import Str
    from poop.types.try_ import Try

    captured: list[object] = []
    ctx = SSL.create_default_context()
    Try(lambda: ctx.load_verify_locations(cadata=Str("not real PEM"))).except_(
        SSL.SSLError, lambda e: captured.append(e.kind())
    ).run()
    assert len(captured) == 1
