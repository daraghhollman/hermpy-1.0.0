from abc import ABC
from pathlib import Path

import pandas as pd
from astropy.table import QTable, Table


class EventList(ABC):

    def __init__(self, table: QTable):
        self.table = table.copy()

        # Maybe perform some checks on the table here. Input tables for lists
        # should not be of length 1.

        # Maybe also some itteration logic? Though that can be handled directly
        # by the astropy table I'm sure


class InstantEventList(EventList):
    def __init__(self, table: QTable, time_column: str):
        super().__init__(table)

        if time_column not in self.table.colnames:
            raise ValueError(
                f"Input table is missing declared time column: {time_column}"
            )

        self.time_column = time_column
        self.table.sort(self.time_column)


class DurationEventList(EventList):
    def __init__(self, table: QTable, start_time_column: str, end_time_column: str):
        super().__init__(table)

        for col in (start_time_column, end_time_column):
            if col not in self.table.colnames:
                raise ValueError(f"Input table is missing declared time column: {col}")

        self.start_time_column = start_time_column
        self.end_time_column = end_time_column


class CrossingList:

    @classmethod
    def from_csv(cls, csv_path: Path, time_column="UTC") -> InstantEventList:

        df = pd.read_csv(csv_path)

        table = Table.from_pandas(df)
        table = QTable(table)

        return InstantEventList(table, time_column=time_column)


class CrossingIntervalList:
    pass
