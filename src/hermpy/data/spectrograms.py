from pathlib import Path

import numpy as np
import xarray as xr
from astropy.time import Time
from sunpy.time import TimeRange


def parse_messenger_fips(file_paths: list[Path], time_range: TimeRange) -> xr.Dataset:

    file_data: list[xr.Dataset] = []
    for path in file_paths:

        # Parse the time
        time_strings = np.genfromtxt(
            path,
            dtype=str,
            usecols=[1],
        )
        times = Time.strptime(
            time_strings,
            format_string="%Y-%jT%H:%M:%S.%f",
            scale="utc",
        ).to_datetime()

        # Parse the data
        # Unit: counts/(s*(keV/e)*cm**2*sr)
        valid_event_flux = np.genfromtxt(
            path, dtype=float, usecols=np.arange(130, 193).tolist()
        )
        # Proton Flux
        proton_flux = np.genfromtxt(
            path, dtype=float, usecols=np.arange(193, 256).tolist()
        )
        # Total Event Flux
        total_event_flux = np.genfromtxt(
            path, dtype=float, usecols=np.arange(256, 319).tolist()
        )

        # Parse metadata
        # A quality value other than zero is indicative of bad data.
        quality = np.genfromtxt(path, dtype=int, usecols=[2])

        # Indicates the FIPS Scan Mode. Tables referenced here are one of the
        # eight E/q stepping tables loaded into the instrument. See the EPPS
        # CDR SIS in the EPPS Document Archive Volume for details. =0 Normal
        # Scan, =1 High Temp Scan, =2 Burst Scan, =3 Test Scan, =4 Table 4, =5
        # Table 5, =6 Table 6, =7 Table 7.
        mode = np.genfromtxt(path, dtype=int, usecols=[3])

        # Remove bad quality data
        if quality.any() != 0:
            # A quality value != 0 is bad, we should ignore these
            # First get the indices, then only keep the rows
            good_quality_indices = np.where(quality == 0)

            times = times[good_quality_indices]
            valid_event_flux = valid_event_flux[good_quality_indices]
            proton_flux = proton_flux[good_quality_indices]
            total_event_flux = total_event_flux[good_quality_indices]

        ds = xr.Dataset(
            data_vars={
                "Proton Flux": (("UTC", "Energy Channel"), proton_flux),
                "Non-Proton Flux": (
                    ("UTC", "Energy Channel"),
                    valid_event_flux - proton_flux,
                ),
                "Mode": mode,
            },
            coords={
                "UTC": times,
                "Energy Channel": np.arange(valid_event_flux.shape[1]),
            },
        )

        file_data.append(ds)

    multi_file_data = xr.concat(file_data, dim="UTC")

    stripped_multi_file_data = multi_file_data.sel(
        UTC=slice(time_range.start.to_datetime(), time_range.end.to_datetime())
    )

    return stripped_multi_file_data


def fips_energy_bin_edges() -> list[float]:
    """Returns calibration for FIPS energy channels. These are bin edges.

    Currently 'calibration' is assumed constant for all data modes.
    This is accepted within the literature and scientific community.


    Returns
    -------
    out : list[float]
        A list with an E/Q value for each of the 64 energy channels.

    """

    # This calibration is from the most recent calibration file
    # on the pds. This is column one.
    # Found here: https://search-pdsppi.igpp.ucla.edu/search/view/?f=yes&id=pds://PPI/mess-epps-fips-calibrated/calibration/FIPA_E2014153CDR_V2&o=1
    calibration = [
        13.5774,
        12.3322,
        11.2011,
        10.1738,
        9.2407,
        8.3930,
        7.6233,
        6.9243,
        6.2892,
        5.7121,
        5.1884,
        4.7126,
        4.2802,
        3.8877,
        3.5310,
        3.2074,
        2.9131,
        2.6459,
        2.4034,
        2.1830,
        1.9828,
        1.8007,
        1.6358,
        1.4855,
        1.3493,
        1.2255,
        1.1133,
        1.0110,
        0.9184,
        0.8343,
        0.7576,
        0.6880,
        0.6251,
        0.5677,
        0.5156,
        0.4682,
        0.4255,
        0.3863,
        0.3510,
        0.3189,
        0.2896,
        0.2631,
        0.2388,
        0.2170,
        0.1970,
        0.1789,
        0.1627,
        0.1478,
        0.1340,
        0.1219,
        0.1107,
        0.1004,
        0.0851,
        0.0729,
        0.0611,
        0.0489,
        0.0371,
        0.0249,
        0.0131,
        0.0087,
        0.0087,
        0.0087,
        0.0087,
        0.0087,
    ]

    return calibration
