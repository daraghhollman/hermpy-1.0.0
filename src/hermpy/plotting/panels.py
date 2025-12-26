# This defers evaluation of type checking until end which allows the circular
# referencing as done in the classes within.
from __future__ import annotations

import matplotlib.pyplot as plt
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
            raise NotImplemented

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


class Panel:
    def __init__(self, table: QTable, time_column: str = "UTC"):
        self.table = table
        self.time_column = time_column

        self._check_units()

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

    @property
    def unit(self):
        return self._unit

    def _check_units(self):
        """
        Tests if the units of each variable in the panel are matching, and
        hence can be plotted together.
        """

        column_units: list[u.Unit] = []
        for column_name in self.table.colnames:

            # Skip time column
            if column_name == self.time_column:
                continue

            column_units.append(self.table[column_name].unit)
            self._unit = self.table[column_name].unit

        # Check only 1 unique unit
        unique_units = set(column_units)
        if len(unique_units) != 1:
            raise ValueError(
                f"Panel data has multiple units: {unique_units}. Cannot add to the same axis!"
            )

    # A panel should have the ability to plot just itself for debug purposes.
    # We separate the drawing to axis, and construction of axis into two
    # separate functions so MultiPanel can create plots for all panels easily.
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

    def plot(self, show=True):
        """
        Creates a quick plot for this panel alone.
        """

        fig, ax = plt.subplots()
        self._plot_on(ax)

        if show:
            plt.show()

        return fig, ax
