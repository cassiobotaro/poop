from __future__ import annotations

# ruff: noqa: S603, S605
import subprocess as _subprocess
from typing import Any, ClassVar

from poop.types.boolean import Boolean
from poop.types.bytes import Bytes
from poop.types.float import Float
from poop.types.int import Int
from poop.types.list import List
from poop.types.none import NoneClass, none
from poop.types.object import Object
from poop.types.path import Path
from poop.types.string import Str
from poop.types.tuple import Tuple


def _unwrap_args(args: List | Str) -> Any:
    if isinstance(args, Str):
        return args._value
    if isinstance(args, List):
        unwrapped: list[Any] = []
        for item in args:
            if isinstance(item, Str):
                unwrapped.append(item._value)
            elif isinstance(item, Path):
                unwrapped.append(str(item))
            else:
                unwrapped.append(item)
        return unwrapped
    return args


def _opt_path(p: Path | Str | None) -> Any:
    if p is None:
        return None
    return p._value if isinstance(p, Str) else str(p)


class CompletedProcess(Object):
    """Wraps Python's `subprocess.CompletedProcess`."""

    __slots__ = ("_impl",)

    def __init__(self, impl: Any) -> None:
        self._impl = impl

    @property
    def returncode(self) -> Int:
        return Int(self._impl.returncode)

    @property
    def args(self) -> Any:
        return self._impl.args

    @property
    def stdout(self) -> Str | Bytes | NoneClass:
        out = self._impl.stdout
        if out is None:
            return none
        return Bytes(out) if isinstance(out, bytes) else Str(out)

    @property
    def stderr(self) -> Str | Bytes | NoneClass:
        err = self._impl.stderr
        if err is None:
            return none
        return Bytes(err) if isinstance(err, bytes) else Str(err)

    def check_returncode(self) -> NoneClass:
        self._impl.check_returncode()
        return none


class Popen(Object):
    """Wraps Python's `subprocess.Popen` — child-process lifecycle."""

    __slots__ = ("_impl",)

    def __init__(self, args: List | Str, **kwargs: Any) -> None:
        self._impl = _subprocess.Popen(_unwrap_args(args), **kwargs)

    @property
    def pid(self) -> Int:
        return Int(self._impl.pid)

    @property
    def returncode(self) -> Int | NoneClass:
        rc = self._impl.returncode
        return none if rc is None else Int(rc)

    def wait(self, timeout: Float | Int | None = None) -> Int:
        t = None if timeout is None else timeout._value
        return Int(self._impl.wait(t))

    def poll(self) -> Int | NoneClass:
        rc = self._impl.poll()
        return none if rc is None else Int(rc)

    def terminate(self) -> NoneClass:
        self._impl.terminate()
        return none

    def kill(self) -> NoneClass:
        self._impl.kill()
        return none

    def send_signal(self, sig: Int) -> NoneClass:
        self._impl.send_signal(sig._value)
        return none

    def communicate(
        self,
        input: Bytes | Str | None = None,
        timeout: Float | Int | None = None,
    ) -> Tuple:
        i = None if input is None else input._value
        t = None if timeout is None else timeout._value
        stdout, stderr = self._impl.communicate(i, t)  # ty: ignore[invalid-argument-type]
        out = (
            none
            if stdout is None
            else (Bytes(stdout) if isinstance(stdout, bytes) else Str(stdout))
        )
        err = (
            none
            if stderr is None
            else (Bytes(stderr) if isinstance(stderr, bytes) else Str(stderr))
        )
        return Tuple(out, err)


class Subprocess:
    """Namespace mirroring Python's `subprocess` module."""

    Popen: ClassVar[type[Popen]] = Popen
    CompletedProcess: ClassVar[type[CompletedProcess]] = CompletedProcess

    # Stream sentinels
    PIPE: ClassVar[Int] = Int(_subprocess.PIPE)
    STDOUT: ClassVar[Int] = Int(_subprocess.STDOUT)
    DEVNULL: ClassVar[Int] = Int(_subprocess.DEVNULL)

    # Errors
    SubprocessError: ClassVar[type[BaseException]] = _subprocess.SubprocessError
    CalledProcessError: ClassVar[type[BaseException]] = _subprocess.CalledProcessError
    TimeoutExpired: ClassVar[type[BaseException]] = _subprocess.TimeoutExpired

    @staticmethod
    def run(
        args: List | Str,
        capture_output: Boolean | None = None,
        check: Boolean | None = None,
        shell: Boolean | None = None,
        cwd: Path | Str | None = None,
        timeout: Float | Int | None = None,
        text: Boolean | None = None,
        input: Bytes | Str | None = None,
    ) -> CompletedProcess:
        kwargs: dict[str, Any] = {}
        if capture_output is not None:
            kwargs["capture_output"] = bool(capture_output)
        if check is not None:
            kwargs["check"] = bool(check)
        if shell is not None:
            kwargs["shell"] = bool(shell)
        if cwd is not None:
            kwargs["cwd"] = _opt_path(cwd)
        if timeout is not None:
            kwargs["timeout"] = timeout._value
        if text is not None:
            kwargs["text"] = bool(text)
        if input is not None:
            kwargs["input"] = input._value
        return CompletedProcess(_subprocess.run(_unwrap_args(args), **kwargs))

    @staticmethod
    def call(args: List | Str, shell: Boolean | None = None) -> Int:
        kwargs: dict[str, Any] = {}
        if shell is not None:
            kwargs["shell"] = bool(shell)
        return Int(_subprocess.call(_unwrap_args(args), **kwargs))

    @staticmethod
    def check_call(args: List | Str, shell: Boolean | None = None) -> Int:
        kwargs: dict[str, Any] = {}
        if shell is not None:
            kwargs["shell"] = bool(shell)
        return Int(_subprocess.check_call(_unwrap_args(args), **kwargs))

    @staticmethod
    def check_output(
        args: List | Str,
        shell: Boolean | None = None,
        text: Boolean | None = None,
    ) -> Bytes | Str:
        kwargs: dict[str, Any] = {}
        if shell is not None:
            kwargs["shell"] = bool(shell)
        if text is not None:
            kwargs["text"] = bool(text)
        result = _subprocess.check_output(_unwrap_args(args), **kwargs)
        return Bytes(result) if isinstance(result, bytes) else Str(result)

    @staticmethod
    def getoutput(cmd: Str) -> Str:
        return Str(_subprocess.getoutput(cmd._value))

    @staticmethod
    def getstatusoutput(cmd: Str) -> Tuple:
        status, output = _subprocess.getstatusoutput(cmd._value)
        return Tuple(Int(status), Str(output))
