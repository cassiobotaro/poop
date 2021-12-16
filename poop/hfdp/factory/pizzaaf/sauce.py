from abc import ABC, abstractmethod


class Sauce(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
