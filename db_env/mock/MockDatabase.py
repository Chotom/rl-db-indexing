from db_env.Database import Database


class MockDatabase(Database):
    """
    Example database class for tests with stored sample data. Does not
    connect with any database, all operations are simulated and perform
    results are already defined.

    Possible states:

    - [0,0,0]
    - [0,0,1]
    - [0,1,1]
    - [1,0,1]
    - [0,1,0]
    - [1,0,0]
    - [1,1,0]
    - [1,1,1]
    """

    database_mutable_cols: dict[str, dict[str, bool]] = {
        "table1": {
            "column1": 0,
            "column2": 0
        },
        "table2": {
            "column1": 0
        }
    }

    def __init__(self):
        super().__init__()

    def get_current_mapped_database(self) -> dict[str, dict[str, bool]]:
        return self.database_mutable_cols

    def execute_action(self, action: int) -> None:
        pass

    def reset_indexes(self) -> None:
        for table_name, cols in self.database_mutable_cols.items():
            for col_name in cols:
                self.database_mutable_cols[table_name][col_name] = 0
