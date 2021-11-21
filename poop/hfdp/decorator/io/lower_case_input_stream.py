from types import TracebackType
from typing import IO, Optional


class LowerCaseInputStream:
    def __init__(self, stream: IO[str]) -> None:
        self.stream = stream

    def read(self, size: int = -1) -> str:
        data = self.stream.read(size)
        return data.lower()

    def __enter__(self) -> "LowerCaseInputStream":
        return self

    def __exit__(
        self,
        exctype: Optional[type[BaseException]],
        excinst: Optional[BaseException],
        exctb: Optional[TracebackType],
    ) -> bool:
        self.stream.close()
        return exctype is None

    def __iter__(self) -> "LowerCaseInputStream":
        return self

    def __next__(self) -> str:
        return next(self.stream).lower()
