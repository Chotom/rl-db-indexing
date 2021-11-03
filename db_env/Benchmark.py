from abc import ABC, abstractmethod


class Benchmark(ABC):
    @abstractmethod
    def prepare_queries(self) -> None:
        """Render queries to be executed during benchmark."""
        raise NotImplementedError

    @abstractmethod
    def execute(self) -> float:
        """:return: QphH metrics measured during executed benchmark."""
        raise NotImplementedError
