class _TranscriptClass:
    def show(self, obj: object) -> None:
        print(str(obj))  # noqa: T201

    def nl(self) -> None:
        print()  # noqa: T201


transcript = _TranscriptClass()
