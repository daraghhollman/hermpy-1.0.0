import datetime as dt

import spiceypy as spice

# hermpy.net introduces a client to handle the caching and fetching of SPICE
# kernels. This makes the management of SPICE kernels very simple using
# spiceypy's context manager.
from hermpy.net import ClientSPICE

spice_client = ClientSPICE()

# There are some default kernels included by default, but more can be added on
# the fly. If you feel your additions would make sense as permanent inclusion,
# please open a PR.

# Here we show an example of adding coordinate systems defined for the
# BepiColombo mission. Allowing us to use "BC_MSO_AB".
spice_client.KERNEL_LOCATIONS.update(
    {
        "BepiColombo Frames": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/pds4/bc/bc_spice/spice_kernels/fk/",
            "PATTERNS": ["bc_sci_v12.tf"],
        }
    }
)

# We open a context in which we load kernels from ClientSPICE. For more details
# see the spiceypy documentation.
with spice.KernelPool(spice_client.fetch()):
    et = spice.datetime2et(dt.datetime(2012, 6, 1))
    position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")

    print(position)

# Equivalently (and preferably), we define a context manager within
# spice_client to perform the same role. All that happens under the hood here
# is that the spice client performs the fetch, passes it to spice.KernelPool(),
# and yields the contextmanager.
with spice_client.KernelPool():
    et = spice.datetime2et(dt.datetime(2012, 6, 1))
    position, _ = spice.spkpos("MESSENGER", et, "BC_MSO_AB", "NONE", "Mercury")

    print(position)
