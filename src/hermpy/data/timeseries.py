from pathlib import Path

from astropy import units as u
from astropy.io import ascii
from astropy.table import QTable, Table, vstack
from astropy.time import Time
from sunpy.time import TimeRange


def main():

    # For testing purposes, lets load some data
    from hermpy.net import ClientMESSENGER

    c = ClientMESSENGER()
    time_range = TimeRange("2011-06-01T00:00", "2011-06-01T01:00")
    c.query(time_range, "MAG")
    file_paths = c.fetch()

    data: QTable = _parse_messenger_mag(file_paths, time_range)

    print(data)


def _parse_messenger_mag(file_paths: list[Path], time_range: TimeRange) -> QTable:

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


if __name__ == "__main__":
    main()
