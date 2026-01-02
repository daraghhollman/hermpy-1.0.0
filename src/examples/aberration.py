from astropy.table import QTable
from sunpy.time import TimeRange

from hermpy.data import parse_messenger_mag, rotate_to_aberrated_coordinates
from hermpy.net import ClientMESSENGER, ClientSPICE

# First we must get some data. Here we fetch MESSENGER MAG and FIPS data for a
# particular time range. For more details on ClientMESSENGER, see
# src/examples/downloading_data.py
c = ClientMESSENGER()
time_range = TimeRange("2011-06-01T00:00", "2011-06-02T01:00")

c.query(time_range, "MAG")
mag_file_paths = c.fetch()

mag_data: QTable = parse_messenger_mag(mag_file_paths, time_range)

# We also require spice kernels for these calculations. For more details see
# src/examples/spice.py
spice_client = ClientSPICE()
with spice_client.KernelPool():

    # We append aberrated terms to mag data in the following way.
    mag_data = rotate_to_aberrated_coordinates(mag_data)

print(
    mag_data[
        [
            "Bx",
            "By",
            "Bz",
            "Bx'",
            "By'",
            "Bz'",
            "Aberration Angle",
        ]
    ]
)
