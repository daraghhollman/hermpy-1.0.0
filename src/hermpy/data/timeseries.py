from pathlib import Path

import numpy as np
from astropy import units as u
from astropy.io import ascii
from astropy.table import QTable, Table, vstack
from astropy.time import Time
from sunpy.time import TimeRange

from hermpy.data.trajectories import get_aberration_angle


def add_field_magnitude(table: QTable) -> QTable:
    """
    A function to add magnetic field magnitude to any QTable with columns 'Bx',
    'By', and 'Bz'.
    Column '|B|' is added to the table.
    """

    new_table = table.copy()

    components = ["Bx", "By", "Bz"]
    new_table["|B|"] = np.sqrt(sum(table[var] ** 2 for var in components))

    return new_table


def rotate_to_aberrated_coordinates(table: QTable, time_column="UTC") -> QTable:
    """
    Add aberrated terms to a timeseries table, rotating around the Z axis by
    the aberration angle (updated daily). Caching of the aberration angle is
    used for quick computation. We assume an average solar wind speed of 400
    km/s.
    """

    times = table[time_column].to_datetime(leap_second_strict="warn")
    aberration_angles: u.Quantity = get_aberration_angle(times)

    # Create rotation matrices
    cos_angles = np.cos(aberration_angles)
    sin_angles = np.sin(aberration_angles)

    rotation_matrices = np.array(
        [
            [
                [c, -s, 0],
                [s, c, 0],
                [0, 0, 1],
            ]
            for c, s in zip(cos_angles, sin_angles)
        ]
    )

    # We want this to work no matter which columns this table includes.
    column_sets = [
        ["X MSO", "Y MSO", "Z MSO"],
        ["X MSM", "Y MSM", "Z MSM"],
        ["Bx", "By", "Bz"],
    ]

    for cols in column_sets:
        # Only process if *all* columns of that exist
        if not all(c in table.colnames for c in cols):
            continue

        # Perform rotation
        data = np.vstack([table[c] for c in cols]).T
        rotated = np.einsum("nij,nj->ni", rotation_matrices, data)

        # Add new columns
        for i, col in enumerate(cols):
            new_name = f"{col}'"

            # We round to 3 decimals to match the data. Its nice to stay
            # consistent, an we don't want to overstate our accuracy.
            table[new_name] = np.round(rotated[:, i], 3)

    table["Aberration Angle"] = np.round(aberration_angles, 3)

    return table


def parse_messenger_mag(file_paths: list[Path], time_range: TimeRange) -> QTable:
    file_data: list[QTable] = []
    for path in file_paths:
        table = ascii.read(path)
        assert type(table) == Table

        # Extract time information
        year = table.columns[0]
        doy = table.columns[1]
        hour = table.columns[2]
        minute = table.columns[3]
        second = table.columns[4]

        yday = [
            f"{y}:{d:03d}:{h:02d}:{m:02d}:{s}"
            for y, d, h, m, s in zip(year, doy, hour, minute, second)
        ]
        time = Time(yday, format="yday", scale="utc")

        # For MESSENGER MAG at full cadence, the files contain 12 columns. Time
        # averaged products contain 16 columns.
        match len(table.colnames):
            # Full Cadence
            case 12:
                file_data.append(
                    QTable(
                        {
                            "UTC": time,
                            "X MSO": table.columns[6] * u.kilometer,
                            "Y MSO": table.columns[7] * u.kilometer,
                            "Z MSO": table.columns[8] * u.kilometer,
                            "Bx": table.columns[9] * u.nanotesla,
                            "By": table.columns[10] * u.nanotesla,
                            "Bz": table.columns[11] * u.nanotesla,
                        }
                    )
                )

            # Averaged Product
            # Note: the time column for averaged data products is at the centre
            # of the averaging window.
            case 16:
                file_data.append(
                    QTable(
                        {
                            "UTC": time,
                            "N Observations": table.columns[6],
                            "X MSO": table.columns[7] * u.kilometer,
                            "Y MSO": table.columns[8] * u.kilometer,
                            "Z MSO": table.columns[9] * u.kilometer,
                            "Bx": table.columns[10] * u.nanotesla,
                            "By": table.columns[11] * u.nanotesla,
                            "Bz": table.columns[12] * u.nanotesla,
                            "SD(Bx)": table.columns[13] * u.nanotesla,
                            "SD(By)": table.columns[14] * u.nanotesla,
                            "SD(Bz)": table.columns[15] * u.nanotesla,
                        },
                        meta={
                            "Notes": "This is an averaged data product. Several observations within a window of time are averaged, with their mean recorded as Bx, By, Bz, and their standard deviation as SD(Bx), etc. UTC marks the centre time of that window, and N Observations details the number of observations in that window."
                        },
                    )
                )
    merged_table = vstack(file_data)

    # Slice this to the time range
    merged_and_sliced_table = merged_table[
        (merged_table["UTC"] > time_range.start)
        & (merged_table["UTC"] < time_range.end)
    ]

    return merged_and_sliced_table
