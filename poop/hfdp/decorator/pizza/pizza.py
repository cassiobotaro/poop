from abc import ABC, abstractmethod


class Pizza(ABC):
    description = "Basic Pizza"

    def get_description(self) -> str:
        return self.description

    @abstractmethod
    def cost(self) -> float:
        raise NotImplementedError
