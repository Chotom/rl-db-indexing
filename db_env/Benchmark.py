from abc import ABC, abstractmethod


class Benchmark(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def prepare_queries(self) -> None:
        """Render queries to be executed during benchmark."""
        raise NotImplementedError

    @abstractmethod
    def run(self) -> float:
        """:return: QphH metrics measured during executed benchmark."""
        raise NotImplementedError
