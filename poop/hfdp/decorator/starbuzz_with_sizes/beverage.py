from abc import ABC, abstractmethod
from enum import Enum


class Beverage(ABC):
    SIZE = Enum("SIZE", "TALL GRANDE VENTI")

    size = SIZE.TALL
    description = "Unknown Beverage"

    def set_size(self, size: SIZE) -> None:
        self.size = size

    def get_size(self) -> SIZE:
        return self.size

    def get_description(self) -> str:
        return self.description

    @abstractmethod
    def cost(self) -> float:
        raise NotImplementedError
