from dataclasses import dataclass, field
from typing import Protocol

import matplotlib.pyplot as plt
import xarray as xr
from astropy.table import Column, QTable

from hermpy.data import parse_messenger_fips


class DataContainer(Protocol):

    # Any data product should be able to be quickly viewed.
    # Quickplot functions should read the metadata for fields
    # such as: x_label, y_label, x_unit.
    def quickplot(self) -> None: ...


@dataclass
class Timeseries(DataContainer):
    table: QTable
    time_column: str = "UTC"
    metadata: dict[str, str] = field(default_factory=dict)

    def quickplot(self) -> None:

        _, ax = plt.subplots()

        # Loop through the non-time columns and plot
        for column_name in self.table.colnames:

            if column_name == self.time_column:
                continue

            x = self.table[self.time_column]
            y = self.table[column_name]

            assert isinstance(x, Column)
            assert isinstance(y, Column)

            ax.plot(x, y, label=column_name)
        plt.show()


@dataclass
class Spectrogram(DataContainer):
    data: xr.Dataset
    time_dimension: str = "UTC"
    metadata: dict[str, str] = field(default_factory=dict)

    def quickplot(self) -> None:

        _, ax = plt.subplots()

        mesh = ax.pcolormesh(
            # Assuming timestamps are right edges, we drop the first data column.
            self.data[1:, ...].T,
        )

        cbar_bounds = (1.02, 0, 0.02, 1)
        cbar_ax = ax.inset_axes(cbar_bounds)
        plt.colorbar(mesh, cax=cbar_ax)

        plt.show()
