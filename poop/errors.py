class PoopError(Exception):
    """Base for all interpreter errors."""


class ParseError(PoopError):
    """Raised when ast.parse fails on source code."""


class ValidationError(PoopError):
    """Raised when a validator rejects the AST."""

    def __init__(self, message: str, lineno: int, col_offset: int) -> None:
        self.lineno = lineno
        self.col_offset = col_offset
        super().__init__(message)

    def __str__(self) -> str:
        return f"{super().__str__()} (line {self.lineno}, col {self.col_offset})"


class TransformError(PoopError):
    """Raised when a transformer fails while rewriting the AST."""

    def __init__(self, message: str, transformer: str) -> None:
        self.transformer = transformer
        super().__init__(message)

    def __str__(self) -> str:
        return f"{super().__str__()} (transformer {self.transformer})"


class ExecutionError(PoopError):
    """Raised when exec() raises during evaluation."""
