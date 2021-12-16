from abc import ABC, abstractmethod


class Pepperoni(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
