from abc import ABC, abstractmethod
from typing import Final, List, Tuple, Dict

from db_env.Benchmark import Benchmark


class Database(ABC):
    """
    Abstract representation of database as an class with methods to fetch states,
    executes actions (changes) and runs prepared benchmark for concrete database.

    - Benchmark: evaluation method executed on database to measure performance.
    - Immutable column: columns with primal key or foreign key - these indexes wont be edited.
    - Mutable column: column where secondary index can be created or dropped.
    """

    def __init__(self, benchmark: Benchmark):
        # Set Database connection
        # Save database immutable indexes (primary keys and foreign keys)
        self._benchmark = benchmark
        self._state = self._get_current_mapped_database()

        self._action_mapper: Final[List[Tuple[str, str, str]]] = [(table_name, col_name, action_type)
                                                                  for table_name, table in self._state.items()
                                                                  for col_name in table
                                                                  for action_type in ['DROP INDEX', 'CREATE INDEX']]

    @property
    def action_mapper(self) -> List[Tuple[str, str, str]]:
        """
        An action_mapper stores possible actions for database in list in format
        [(table_name, column_name, action_type)], where index is action number.

        Example:
        --------
        >>> db = Database()
        >>> db.action_mapper
        [('table1', 'column1', 'DROP INDEX'),
        ('table1', 'column1', 'CREATE INDEX'),
        ('table1', 'column2', 'DROP INDEX'),
        ('table1', 'column2', 'CREATE INDEX')]

        :return: possible actions for every column in tables
        """
        return self._action_mapper

    @property
    def state(self) -> Dict[str, Dict[str, bool]]:
        """
        Represents database schema as dictionary object with keys as table and
        column name, set boolean value as is column indexed info. Set 1 if
        index is created on column and 0 if column is not indexed.

        Example:
        --------
        >>> db = Database()
        >>> db.state
        {
            "table_name": {
                "column_name": 1, # is indexed
                "column_name2": 0 # without index
            },
            "table_name2": {
                "column_name": 1, # is indexed
                "column_name2": 1 # is indexed
            }
        }

        :return: State as mapped database to dict[str, dict[str, bool]] type
        """
        return self._state

    @abstractmethod
    def execute_action(self, action: int) -> None:
        """
        Execute index changes in database defined by action from action_mapper
        and update state property.
        """
        raise NotImplementedError

    @abstractmethod
    def execute_benchmark(self) -> float:
        """:return: QphH metrics measured during executed benchmark."""
        raise NotImplementedError

    @abstractmethod
    def reset_indexes(self) -> None:
        """Drop indexes from all mutable columns in database."""
        raise NotImplementedError

    @abstractmethod
    def _get_current_mapped_database(self) -> Dict[str, Dict[str, bool]]:
        """Fetch current database schema and map mutable columns to dictionary object."""
        raise NotImplementedError
