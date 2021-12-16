from abc import ABC, abstractmethod


class Veggies(ABC):
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError
