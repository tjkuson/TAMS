"""
This files classes to represent data from the database to the user.
"""

import logging
from typing import Any

from .database_model import Database
from .exceptions import MissingTables


class DatabaseView:
    """Represent data from the database."""

    def __init__(self, connection_string: str) -> None:
        """Initialize database view and connect to database."""

        self.connection_string: str = connection_string
        with Database(self.connection_string) as database:
            if database.conn.closed:
                raise ConnectionError("Unable to connect to database")
            logging.info("Connection to database in DatabaseView successful.")

    def get_tables(self) -> list[tuple]:
        """Get list of tables in the database."""

        query: str = "select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE';"
        with Database(self.connection_string) as database:
            database.exec(query)
            return database.cur.fetchall()

    def validate_tables(self) -> None:
        """Validate tables in the database; raises an exception if they are not valid."""

        # Check the required tables exist
        tables_needed: set[tuple] = {
            ("project",),
        }
        tables_present: set[tuple] = set(self.get_tables())
        missing_tables: set[tuple] = tables_needed - tables_present
        if missing_tables:
            raise MissingTables(missing_tables)

    def view_select_from_where(
        self, select_value: str, from_value: str, *where_value: tuple[str] | str
    ) -> tuple[list[tuple], tuple[str, ...]]:
        """Return selection."""

        # Construct SQL query
        query = f"select {select_value} from {from_value}"
        if where_value:
            # Get rid of trailing comma in tuple
            where_value_formatted: str = ",".join([str(x) for x in where_value])
            query = f"{query} where {where_value_formatted}"
        query = f"{query};"

        # Get data
        with Database(self.connection_string) as database:
            database.exec(query)
            data: list[tuple] = database.cur.fetchall()
        if select_value == "*":
            # TODO: Deal with wildcard select.
            raise Exception("Wildcard selects not supported yet!")
        column_headers: tuple[str, ...] = tuple(
            select_value.replace(" ", "").split(",")
        )

        return data, column_headers

    def get_version(self) -> str:
        """Get database version."""

        query: str = "select version();"
        with Database(self.connection_string) as database:
            database.exec(query)
            version: str = str(database.cur.fetchone())
        return version

    def get_project_metadata(
        self, project_id: int
    ) -> tuple[tuple[Any, ...], tuple[str, ...]]:
        """Get project metadata."""

        data, column_headers = self.view_select_from_where(
            "project_id, title, project_type, summary, keyword, start_date, end_date, directory_path",
            "project",
            f"project_id={project_id}",
        )

        # Get metadata from specific row
        row_data: tuple[Any, ...] = data[0]

        return row_data, column_headers

    def get_user_metadata(
        self, user_id: int
    ) -> tuple[tuple[Any, ...], tuple[str, ...]]:
        """Get user metadata."""

        data, column_headers = self.view_select_from_where(
            "user_id, first_name, last_name, email_address",
            '"user"',
            f"user_id={user_id}",
        )

        # Get metadata from specific row
        row_data: tuple[Any, ...] = data[0]

        return row_data, column_headers

    def get_scan_metadata(
        self, scan_id: int
    ) -> tuple[tuple[Any, ...], tuple[str, ...]]:
        """Get scan metadata."""

        data, column_header = self.view_select_from_where(
            "scan_id, project_id, instrument_id",
            "scan",
            f"scan_id={scan_id}",
        )

        # Can't edit a tuple, so turn the tuple into a list
        row: tuple[Any, ...] = tuple(data[0])

        # Get project title
        project_id: int = row[1]
        project_data, _ = self.view_select_from_where(
            "title",
            "project",
            f"project_id={project_id}",
        )
        project_title: str = project_data[0][0]

        # Add project title to project id metadata
        project_id_metadata = f"{project_id} ({project_title})"

        # Get instrument name
        instrument_id: int = row[2]
        instrument_data, _ = self.view_select_from_where(
            "name",
            "instrument",
            f"instrument_id={instrument_id}",
        )
        instrument_name: str = instrument_data[0][0]

        # Add instrument name to instrument id metadata
        instrument_id_metadata = f"{instrument_id} ({instrument_name})"

        # Turn the list back into a tuple, the expected return value
        updated_row: tuple = (scan_id, project_id_metadata, instrument_id_metadata)
        return updated_row, column_header
