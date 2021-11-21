from abc import ABC, abstractmethod


class Beverage(ABC):

    description = "Unknown Beverage"

    def get_description(self) -> str:
        return self.description

    @abstractmethod
    def cost(self) -> float:
        raise NotImplementedError
