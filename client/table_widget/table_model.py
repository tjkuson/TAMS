"""Define a table model used in the GUI.

The model handles providing the data for display by the view. We write a custom model which is a subclass of
QAbstractTableModel.

The reason for using a custom model over the built-in models is for greater control over
data representation.
"""

from datetime import date, datetime
from typing import Any, Union

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt


class TableModel(QAbstractTableModel):
    """Define the custom table model, a subclass of a built-in Qt abstract model."""

    def __init__(self, data: list[tuple], column_headers: list[str]):
        super().__init__()
        # Anticipate a list of tuples, as this is what database returns upon select.
        self._data = data
        self._column_headers = column_headers

    def data(
        self,
        index: Union[QModelIndex, QPersistentModelIndex],
        role: int = ...,
    ) -> Any:
        """Returns presentation information for given locations in the table."""

        if role == Qt.DisplayRole:
            # Get the raw value
            # .row() indexes the outer list; .column() indexes the sub-list
            value = self._data[index.row()][index.column()]

            # Perform per-type checks and render accordingly.
            if isinstance(value, (datetime, date)):
                # Render time to YYY-MM-DD
                return f"{value:%Y-%m-%d}"
            if isinstance(value, float):
                return f"{value:.2f}"
            if isinstance(value, (str, int)):
                return f"{value}"

            # Value was not captured above
            return "Error"

        return None

    def rowCount(self, *args, **kwargs) -> int:
        """Return the length of the outer list."""
        return len(self._data)

    def columnCount(self, *args, **kwargs) -> int:
        """Take the first sub-list and return the length.

        This only works if all the rows are of equal length.
        """
        return len(self._data[0])

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:
        """Return the header data."""

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                header: str = str(self._column_headers[section])
                return header
        # Not returning this makes headers not show, for whatever reason.
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def get_row_data(self, row_index: int) -> tuple[Any, ...]:
        """Return the row from a given row index."""
        return self._data[row_index]
