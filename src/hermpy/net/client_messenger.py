import calendar
import datetime as dt
from typing import Any

from astropy.time import Time
from astropy.utils.data import download_files_in_parallel
from sunpy.net import Scraper
from sunpy.time import TimeRange


def main():
    """
    An example of how this class might be used in practice.

    Downloads are cached in ~/.hermpy/cache
    """

    client = ClientMESSENGER()

    client.query(TimeRange("2011-06-01", "2011-06-02"), "MAG")

    # We can access files with this function.
    local_paths = client.download()

    print(local_paths)


class ClientMESSENGER:

    def __init__(
        self,
        PDS_BASE_URL: str = "https://pds-ppi.igpp.ucla.edu/data/",
        PDS_DATA_LOCATION: dict[str, Any] = {
            "MAG": "mess-mag-calibrated/data/mso/",
            "MAG 1s": "mess-mag-calibrated/data/mso-avg/",
            "MAG 5s": "mess-mag-calibrated/data/mso-avg/",
            "MAG 10s": "mess-mag-calibrated/data/mso-avg/",
            "MAG 60s": "mess-mag-calibrated/data/mso-avg/",
        },
        FILE_PATTERN: dict[str, str] = {
            "MAG": "{{year:4d}}/{subdir}/MAGMSOSCI{{year:2d}}{{day_of_year:3d}}_V{{version}}.TAB",
            "MAG 1s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_01_V{{version}}.TAB",
            "MAG 5s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_05_V{{version}}.TAB",
            "MAG 10s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_10_V{{version}}.TAB",
            "MAG 60s": "{{year:4d}}/{subdir}/MAGMSOSCIAVG{{year:2d}}{{day_of_year:3d}}_60_V{{version}}.TAB",
        },
    ):
        # Paths defining where the data can be found
        self.PDS_BASE_URL = PDS_BASE_URL
        self.PDS_DATA_LOCATION = PDS_DATA_LOCATION
        self.FILE_PATTERN = FILE_PATTERN

        # We want the user to be able to query for the existance of
        # files before downloading, so we introduce a search buffer to
        # hold the results of the most recent query.
        self._query_buffer: list[str] = []

    @property
    def instruments(self) -> list[str]:
        return list(self.PDS_DATA_LOCATION.keys())

    def query(self, time_range: TimeRange, instrument: str) -> list[str]:
        """
        Query the data locations for key <instrument>, between the times in
        time_range.

        Returns a list[str] of urls and extends the search buffer.
        """

        pattern = (
            f"{self.PDS_BASE_URL}{self.PDS_DATA_LOCATION[instrument]}/"
            f"{self.FILE_PATTERN[instrument]}"
        )

        subdir = _get_subdir(time_range)

        if isinstance(subdir, list):
            urls: list[Any] = []
            for s in subdir:

                pattern_kwargs = {
                    "subdir": s,
                }

                scraper = Scraper(format=pattern, **pattern_kwargs)
                filelist = scraper.filelist(time_range)
                assert type(filelist) == list
                urls.extend(filelist)

        else:
            pattern_kwargs = {
                "subdir": subdir,
            }

            scraper = Scraper(format=pattern, **pattern_kwargs)
            filelist = scraper.filelist(time_range)
            assert type(filelist) == list
            urls = filelist

        # For some reason, this gives us more than just the files we want.
        # We need to get a list of all the day of years in our time range
        # and compare.
        doys = _get_timerange_doys(time_range)
        urls = [url for url in urls if any(doy in url.split("/")[-1] for doy in doys)]

        # Add urls to search buffer
        self._query_buffer.extend(urls)

        return urls

    def download(self, check_for_updates: bool = False) -> list:
        """
        Download files in self.query_buffer and clears the buffer.
        """

        data_paths = download_files_in_parallel(
            self._query_buffer,
            cache="update" if check_for_updates else True,
            pkgname="hermpy",
        )

        # Flush query buffer
        self._query_buffer = []

        return data_paths


def _get_subdir(time_range: TimeRange) -> str | list[str]:
    """
    Determine the MAG subdirectories required for a given time range.
    """

    # We only need to work with the dates
    start_date = time_range.start.datetime.date()
    end_date = time_range.end.datetime.date()

    # We need to work month by month for the time range:
    subdirs: list[str] = []

    month_start_date = dt.date(start_date.year, start_date.month, 1)

    while month_start_date <= end_date:
        year, month = month_start_date.year, month_start_date.month

        first_day = dt.date(year, month, 1)
        last_day = dt.date(year, month, calendar.monthrange(year, month)[1])

        start_doy = first_day.timetuple().tm_yday
        end_doy = last_day.timetuple().tm_yday

        month_str = calendar.month_abbr[month].upper()

        subdirs.append(f"{start_doy:03d}_{end_doy:03d}_{month_str}")

        # Advance to next month
        if month == 12:
            month_start_date = dt.date(year + 1, 1, 1)
        else:
            month_start_date = dt.date(year, month + 1, 1)

    return subdirs[0] if len(subdirs) == 1 else subdirs


def _get_timerange_doys(time_range: TimeRange) -> list[int]:
    """
    For a given TimeRange return the day-of-years it spans. Can result in a
    list of length one, this is wanted behaviour.
    """

    dates: list[Time] = time_range.get_dates()

    doys = [date.strftime("%j") for date in dates]

    return doys


if __name__ == "__main__":
    main()
