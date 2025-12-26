from astropy.table import QTable
from sunpy.time import TimeRange

from hermpy.data import parse_messenger_mag
from hermpy.net import ClientMESSENGER
from hermpy.plotting import Panel
from hermpy.plotting.panels import MultiPanel

# First we must get some data. Here we fetch MESSENGER MAG data.
c = ClientMESSENGER()
time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")
c.query(time_range, "MAG")
file_paths = c.fetch()

data: QTable = parse_messenger_mag(file_paths, time_range)

# Adding this data as it is to a Panel object will result in an error, as the
# columns (other than the time column) have multiple units, and can't be
# represented on the same axis.

# We hence need to shorten this table to just the columns we want in this Panel.
data.keep_columns(["UTC", "Bx", "By", "Bz"])
mag_panel = Panel(data)

# The temporary figure and axis are returned for further usage.
fig, ax = mag_panel.plot()

# However, we can combine Panel objects to construct a multi-panel
# plot by simply adding them.

# Lets make a second panel where we plot just Bx
data: QTable = parse_messenger_mag(file_paths, time_range)
data.keep_columns(["UTC", "Bx"])
bx_panel = Panel(data)

# We can combine these using the add operator.
multipanel: MultiPanel = mag_panel + bx_panel
fig, axes = multipanel.plot()

# You can also add multipanels to the same effect.
multipanel += multipanel
multipanel.plot()
