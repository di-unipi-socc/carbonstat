from abc import ABC, abstractmethod

# Abstract carbon-aware strategy
class CarbonAwareStrategy(ABC):
    @abstractmethod
    def get() -> str:
        pass