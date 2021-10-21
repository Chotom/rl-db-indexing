from abc import ABC, abstractmethod
from typing import Final

from db_env.Benchmark import Benchmark


class Database(ABC):
    """
    Abstract representation of database as an class with methods to fetch states,
    executes actions (changes) and runs prepared benchmark for concrete database.

    - Benchmark: evaluation method executed on database to measure performance.
    - Immutable column: columns with primal key or foreign key - these indexes wont be edited.
    - Mutable column: column where secondary index can be created or dropped.
    """

    def __init__(self):
        # Set Database connection
        # Save database immutable indexes (primary keys and foreign keys)
        # self._benchmark = benchmark
        self._action_mapper: Final[list[(str, str, str)]] = [(table_name, col_name, action_type)
                                                             for table_name, table in
                                                             self.get_current_mapped_database().items()
                                                             for col_name in table
                                                             for action_type in ['DROP', 'CREATE']]

    @abstractmethod
    def get_current_mapped_database(self) -> dict[str, dict[str, bool]]:
        """
        Fetch current database schema and map mutable columns to dictionary object
        with keys as table and column name and set boolean value as is column
        indexed info. Set 1 if index is created on column and 0 if column is not indexed.

        Example:
        --------
        >>> db = Database()
        >>> db.get_current_mapped_database()
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

        :return: Mapped database to dict[str, dict[str, bool]] type
        """
        raise NotImplementedError

    @abstractmethod
    def execute_action(self, action: int) -> None:
        """Execute index changes in database defined by action from action_mapper."""
        raise NotImplementedError

    @abstractmethod
    def reset_indexes(self) -> None:
        """Drop indexes from all mutable columns in database."""
        raise NotImplementedError

    @property
    def action_mapper(self) -> list[(str, str, str)]:
        """
        An action_mapper stores possible actions for database in list in format
        [(table_name, column_name, action_type)], where index is action number.

        Example:
        --------
        >>> db = Database()
        >>> db.action_mapper
        [('table1', 'column1', 'DROP'),
        ('table1', 'column1', 'CREATE'),
        ('table1', 'column2', 'DROP'),
        ('table1', 'column2', 'CREATE')]

        :return: possible actions for every column in tables
        """
        return self._action_mapper
