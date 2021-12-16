from abc import ABC, abstractmethod


class Clams(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
