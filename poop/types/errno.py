import errno as _errno
from typing import ClassVar

from poop.types.dict import Dict
from poop.types.int import Int
from poop.types.string import Str


def _build_errorcode() -> Dict:
    d = Dict()
    for code, name in _errno.errorcode.items():
        d.at_put(Int(code), Str(name))
    return d


class Errno:
    """Namespace mirroring Python's `errno` module.

    Every public integer constant in `errno.*` (`EPERM`, `ENOENT`,
    `EAGAIN`, …) is exposed as a POOP `Int` class attribute under
    the same name. `errno.errorcode` maps each canonical code to its
    POOP `Str` name. Aliases that share a code (`EDEADLK`/`EDEADLOCK`,
    `EWOULDBLOCK`/`EAGAIN`, `EOPNOTSUPP`/`ENOTSUP`) are bound under
    every name Python exposes; `errorcode` only carries the canonical
    one.

    Class attributes are forward-declared statically (so type checkers
    see them) and assigned dynamically below from whichever subset
    CPython exposes on the host — POOP automatically tracks Linux /
    macOS / Windows differences without per-platform conditionals.
    """

    errorcode: ClassVar[Dict] = _build_errorcode()

    E2BIG: ClassVar[Int]
    EACCES: ClassVar[Int]
    EADDRINUSE: ClassVar[Int]
    EADDRNOTAVAIL: ClassVar[Int]
    EADV: ClassVar[Int]
    EAFNOSUPPORT: ClassVar[Int]
    EAGAIN: ClassVar[Int]
    EALREADY: ClassVar[Int]
    EBADE: ClassVar[Int]
    EBADF: ClassVar[Int]
    EBADFD: ClassVar[Int]
    EBADMSG: ClassVar[Int]
    EBADR: ClassVar[Int]
    EBADRQC: ClassVar[Int]
    EBADSLT: ClassVar[Int]
    EBFONT: ClassVar[Int]
    EBUSY: ClassVar[Int]
    ECANCELED: ClassVar[Int]
    ECHILD: ClassVar[Int]
    ECHRNG: ClassVar[Int]
    ECOMM: ClassVar[Int]
    ECONNABORTED: ClassVar[Int]
    ECONNREFUSED: ClassVar[Int]
    ECONNRESET: ClassVar[Int]
    EDEADLK: ClassVar[Int]
    EDEADLOCK: ClassVar[Int]
    EDESTADDRREQ: ClassVar[Int]
    EDOM: ClassVar[Int]
    EDOTDOT: ClassVar[Int]
    EDQUOT: ClassVar[Int]
    EEXIST: ClassVar[Int]
    EFAULT: ClassVar[Int]
    EFBIG: ClassVar[Int]
    EHOSTDOWN: ClassVar[Int]
    EHOSTUNREACH: ClassVar[Int]
    EHWPOISON: ClassVar[Int]
    EIDRM: ClassVar[Int]
    EILSEQ: ClassVar[Int]
    EINPROGRESS: ClassVar[Int]
    EINTR: ClassVar[Int]
    EINVAL: ClassVar[Int]
    EIO: ClassVar[Int]
    EISCONN: ClassVar[Int]
    EISDIR: ClassVar[Int]
    EISNAM: ClassVar[Int]
    EKEYEXPIRED: ClassVar[Int]
    EKEYREJECTED: ClassVar[Int]
    EKEYREVOKED: ClassVar[Int]
    EL2HLT: ClassVar[Int]
    EL2NSYNC: ClassVar[Int]
    EL3HLT: ClassVar[Int]
    EL3RST: ClassVar[Int]
    ELIBACC: ClassVar[Int]
    ELIBBAD: ClassVar[Int]
    ELIBEXEC: ClassVar[Int]
    ELIBMAX: ClassVar[Int]
    ELIBSCN: ClassVar[Int]
    ELNRNG: ClassVar[Int]
    ELOOP: ClassVar[Int]
    EMEDIUMTYPE: ClassVar[Int]
    EMFILE: ClassVar[Int]
    EMLINK: ClassVar[Int]
    EMSGSIZE: ClassVar[Int]
    EMULTIHOP: ClassVar[Int]
    ENAMETOOLONG: ClassVar[Int]
    ENAVAIL: ClassVar[Int]
    ENETDOWN: ClassVar[Int]
    ENETRESET: ClassVar[Int]
    ENETUNREACH: ClassVar[Int]
    ENFILE: ClassVar[Int]
    ENOANO: ClassVar[Int]
    ENOBUFS: ClassVar[Int]
    ENOCSI: ClassVar[Int]
    ENODATA: ClassVar[Int]
    ENODEV: ClassVar[Int]
    ENOENT: ClassVar[Int]
    ENOEXEC: ClassVar[Int]
    ENOKEY: ClassVar[Int]
    ENOLCK: ClassVar[Int]
    ENOLINK: ClassVar[Int]
    ENOMEDIUM: ClassVar[Int]
    ENOMEM: ClassVar[Int]
    ENOMSG: ClassVar[Int]
    ENONET: ClassVar[Int]
    ENOPKG: ClassVar[Int]
    ENOPROTOOPT: ClassVar[Int]
    ENOSPC: ClassVar[Int]
    ENOSR: ClassVar[Int]
    ENOSTR: ClassVar[Int]
    ENOSYS: ClassVar[Int]
    ENOTBLK: ClassVar[Int]
    ENOTCONN: ClassVar[Int]
    ENOTDIR: ClassVar[Int]
    ENOTEMPTY: ClassVar[Int]
    ENOTNAM: ClassVar[Int]
    ENOTRECOVERABLE: ClassVar[Int]
    ENOTSOCK: ClassVar[Int]
    ENOTSUP: ClassVar[Int]
    ENOTTY: ClassVar[Int]
    ENOTUNIQ: ClassVar[Int]
    ENXIO: ClassVar[Int]
    EOPNOTSUPP: ClassVar[Int]
    EOVERFLOW: ClassVar[Int]
    EOWNERDEAD: ClassVar[Int]
    EPERM: ClassVar[Int]
    EPFNOSUPPORT: ClassVar[Int]
    EPIPE: ClassVar[Int]
    EPROTO: ClassVar[Int]
    EPROTONOSUPPORT: ClassVar[Int]
    EPROTOTYPE: ClassVar[Int]
    ERANGE: ClassVar[Int]
    EREMCHG: ClassVar[Int]
    EREMOTE: ClassVar[Int]
    EREMOTEIO: ClassVar[Int]
    ERESTART: ClassVar[Int]
    ERFKILL: ClassVar[Int]
    EROFS: ClassVar[Int]
    ESHUTDOWN: ClassVar[Int]
    ESOCKTNOSUPPORT: ClassVar[Int]
    ESPIPE: ClassVar[Int]
    ESRCH: ClassVar[Int]
    ESRMNT: ClassVar[Int]
    ESTALE: ClassVar[Int]
    ESTRPIPE: ClassVar[Int]
    ETIME: ClassVar[Int]
    ETIMEDOUT: ClassVar[Int]
    ETOOMANYREFS: ClassVar[Int]
    ETXTBSY: ClassVar[Int]
    EUCLEAN: ClassVar[Int]
    EUNATCH: ClassVar[Int]
    EUSERS: ClassVar[Int]
    EWOULDBLOCK: ClassVar[Int]
    EXDEV: ClassVar[Int]
    EXFULL: ClassVar[Int]


for _name in dir(_errno):
    if _name.startswith("_") or _name == "errorcode":
        continue
    _value = getattr(_errno, _name)
    if isinstance(_value, int):
        setattr(Errno, _name, Int(_value))
