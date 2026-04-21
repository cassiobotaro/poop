class _TranscriptClass:
    def show(self, obj: object) -> _TranscriptClass:
        print(str(obj))  # noqa: T201
        return self

    def nl(self) -> _TranscriptClass:
        print()  # noqa: T201
        return self


transcript = _TranscriptClass()
