# This defers evaluation of type checking until end which allows the circular
# referencing as done in the classes within.
from __future__ import annotations

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from astropy import units as u
from astropy.table import QTable


class MultiPanel:
    def __init__(self, panels: list[Panel]):
        self._panels = panels

    def __add__(self, other) -> MultiPanel:
        # Used to add a Panel to the end of this multipanel.
        if isinstance(other, MultiPanel):
            return MultiPanel([*self._panels, *other._panels])

        elif isinstance(other, Panel):
            return MultiPanel([*self._panels, other])

        else:
            raise NotImplementedError

    def plot(self, sharex=True, show=True, figsize: tuple[int, int] | None = None):
        n = len(self._panels)

        fig, axes = plt.subplots(
            nrows=n,
            ncols=1,
            sharex=sharex,
            figsize=figsize or (8, 2.5 * n),
        )

        # Handle single-panel edge case
        if n == 1:
            axes = [axes]

        for panel, ax in zip(self._panels, axes):
            panel._plot_on(ax)

        if show:
            plt.show()

        return fig, axes


class Panel(ABC):
    """Base class for all panel types."""

    def __init__(self, time_column: str = "UTC"):
        self.time_column = time_column

    def __add__(self, other) -> MultiPanel:
        # If other is another Panel, we can just pass this Panel and the
        # other as a list to a new Multipanel.
        if isinstance(other, Panel):
            return MultiPanel([self, other])
        # Otherwise, we need to reconstruct the MultiPanel object with this
        # panel as the first one.
        elif isinstance(other, MultiPanel):
            multipanel: MultiPanel = other
            return MultiPanel([self, *multipanel._panels])
        else:
            return NotImplemented

    # A panel should have the ability to plot just itself for debug purposes.
    # We separate the drawing to axis, and construction of axis into two
    # separate functions so MultiPanel can create plots for all panels easily.
    @abstractmethod
    def _plot_on(self, ax):
        """Plot panel content on the given axis."""
        pass

    def plot(self, show=True):
        """Creates a quick plot for this panel alone."""

        fig, ax = plt.subplots()
        self._plot_on(ax)

        if show:
            plt.show()

        return fig, ax


class TimeseriesPanel(Panel):
    def __init__(self, table: QTable, time_column: str = "UTC"):
        super().__init__(time_column)
        self.table = table
        self._check_units()

    @property
    def unit(self):
        return self._unit

    def _check_units(self):
        """
        Tests if the units of each variable in the panel are matching, and
        hence can be plotted together.
        """

        units = []

        for column_name in self.table.colnames:
            # Skip the time column
            if column_name == self.time_column:
                continue

            unit = self.table[column_name].unit
            units.append(unit)

        base_unit = units[0]

        for unit in units[1:]:
            if not unit.is_equivalent(base_unit):
                raise ValueError(f"Panel data has multiple incompatible units: {units}")

        self._unit = base_unit

    def _plot_on(self, ax):
        for column_name in self.table.colnames:
            if column_name == self.time_column:
                continue

            ax.plot(
                self.table[self.time_column].to_datetime(),
                self.table[column_name].value,
                label=column_name,
            )

        ax.set_ylabel(self.unit.to_string())
        ax.legend()


class SpectrogramPanel(Panel):
    """
    A class for drawing 2D panels. We call it SpectrogramPanel, but it is
    general to any channel variable, e.g. energy, frequency, etc.
    """

    def __init__(
        self,
        data: xr.DataArray,
        time_dim: str = "UTC",
        y_dim: str = "Energy Channel",
        y_bin_edges: list[float | int] | None = None,
        vmin=None,
        vmax=None,
        cmap="viridis",
        yscale="log",
    ):
        self.data = data
        self.time_dim = time_dim
        self.y_dim = y_dim
        self.y_bin_edges = y_bin_edges or np.arange(0, len(data[y_dim]) + 1).tolist()
        self.vmin = vmin
        self.vmax = vmax
        self.cmap = cmap
        self.yscale = yscale

    def _plot_on(self, ax):
        mesh = ax.pcolormesh(
            # Assuming timestamps are right edges, we drop the first data column.
            self.data[self.time_dim],
            self.y_bin_edges,
            self.data[1:, ...].T,
            vmin=self.vmin,
            vmax=self.vmax,
            cmap=self.cmap,
        )

        cbar_bounds = [1.02, 0, 0.02, 1]
        self.cbar_ax = ax.inset_axes(cbar_bounds)

        self.cbar = plt.colorbar(mesh, cax=self.cbar_ax)

        ax.set_yscale(self.yscale)
