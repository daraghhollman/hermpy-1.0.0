import numpy as np
import spiceypy as spice

import astropy.units as u
from astropy.table import QTable, vstack, hstack
from astropy.time import Time
from hermpy.net import ClientSPICE
from hermpy.utils import Constants as c # Need for 'Mercury Radii' unit


Zd = c.DIPOLE_OFFSET.to("Mercury Radii")

spice_client = ClientSPICE()

spice_client.KERNEL_LOCATIONS.update(
    {
        "MESSENGER Frames (tf)": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/fk/",
            "PATTERNS": ["msgr_dyn_v600.tf"],
        },
        "MESSENGER": {
            "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
            "DIRECTORY": "pds/data/mess-e_v_h-spice-6-v1.0/messsp_1000/data/spk/",
            "PATTERNS": ["msgr_??????_??????_??????_od431sc_2.bsp"],
        },
    }
)


def parse_spice(time_array, units="Mercury Radii", frame="MSO"):
    """
    Queries SPICE for MESSENGER's position relative to Mercury at each given
    time, and returns it as a table in the requested reference frame/units.

    time_array: array-like of times (anything astropy.time.Time can parse)
        to query positions for. Must lie within the MESSENGER mission
        timespan (mission_start to mission_end).
    units: unit to convert the position columns to (e.g. "Mercury Radii",
        "km"). "UTC" column is left untouched.
    frame: coordinate frame to return positions in.
        "MSO" - Mercury Solar Orbital
        "MSM" - Mercury Solar Magnetospheric (MSO shifted along Z by the
                dipole offset Zd)
        "All" - both MSO and MSM columns included

    Returns:
        table: QTable with "UTC", "|R|" (distance to Mercury), and position
            columns for the requested frame(s).
    """
    time = Time(time_array).to_datetime()


    # Convert to ephemeris time and query spacecraft position relative to Mercury
    et = spice.datetime2et(time)
    position, _ = spice.spkpos("MESSENGER", et, "MSGR_MSO", "NONE", "Mercury")

    print('Loaded data')

    X_MSO = np.array([pos[0] for pos in position])
    Y_MSO = np.array([pos[1] for pos in position])
    Z_MSO = np.array([pos[2] for pos in position])


    if frame == "MSO":
        table = QTable({
            "UTC" : Time(time),
            "X MSO" : X_MSO * u.Unit("km"),
            "Y MSO" : Y_MSO * u.Unit("km"),
            "Z MSO" : Z_MSO * u.Unit("km"),
            })

    elif frame == "MSM":
        # Shift Z by the dipole offset to convert MSO -> MSM
        table = QTable({
            "UTC" : Time(time),
            "X MSM" : X_MSO * u.Unit("km"),
            "Y MSM" : Y_MSO * u.Unit("km"),
            "Z MSM" : Z_MSO * u.Unit("km") - Zd.to("km"),
            })

    elif frame == "All":
        table = QTable({
            "UTC" : Time(time),
            "X MSO" : X_MSO * u.Unit("km"),
            "Y MSO" : Y_MSO * u.Unit("km"),
            "Z MSO" : Z_MSO * u.Unit("km"),
            "X MSM" : X_MSO * u.Unit("km"),
            "Y MSM" : Y_MSO * u.Unit("km"),
            "Z MSM" : Z_MSO * u.Unit("km") - Zd.to("km"),
            })
    else:
        raise ValueError("Invalid frame, not one of 'MSO', 'MSM', or 'All'")

    # Convert all non-UTC columns to the requested output units
    if units != "km":
        for col in table.keys():
            if col == "UTC":
                continue
            else:
                table[col] = table[col].to(units)

    return table
