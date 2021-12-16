from abc import ABC, abstractmethod


class Cheese(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
