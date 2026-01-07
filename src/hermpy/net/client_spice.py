import re
from contextlib import contextmanager
from fnmatch import fnmatch
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import spiceypy as spice
from astropy.utils.data import download_files_in_parallel


class ClientSPICE:
    def __init__(
        self,
        KERNEL_LOCATIONS: dict[str, dict[str, Any]] = {
            "Generic (tls)": {
                "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
                "DIRECTORY": "generic_kernels/lsk/",
                "PATTERNS": ["naif????.tls", "latest_leapseconds.tls"],
            },
            "Generic (tpc)": {
                "BASE": "https://naif.jpl.nasa.gov/pub/naif/",
                "DIRECTORY": "generic_kernels/pck/",
                "PATTERNS": ["pck00011.tpc"],
            },
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
        },
    ):
        self.KERNEL_LOCATIONS = KERNEL_LOCATIONS
        self._query_buffer: list[str] = []

    def fetch(self, check_for_updates: bool = False) -> list[Path]:
        """
        Download and fetch files in self.query_buffer and clears the buffer. If
        files are already downloaded, fetch them.
        """

        all_urls: list[str] = []

        for cfg in self.KERNEL_LOCATIONS.values():
            base = cfg["BASE"]
            directory = cfg["DIRECTORY"]
            patterns = cfg["PATTERNS"]

            all_urls.extend(expand_patterns(base, directory, patterns))

        self._query_buffer.extend(all_urls)

        data_paths = download_files_in_parallel(
            self._query_buffer,
            cache="update" if check_for_updates else True,
            pkgname="hermpy",
        )

        # Flush query buffer
        self._query_buffer = []

        return data_paths

    # We want this class to be able to function as a spiceypy.KernelPool()
    @contextmanager
    def KernelPool(self):
        with spice.KernelPool(self.fetch()):
            yield


def list_remote_files(url: str) -> list[str]:
    """Return filenames from a simple Apache-style directory listing."""

    with urlopen(url) as f:
        html = f.read().decode("utf-8")

    # Extract href targets
    return re.findall(r'href="([^"/]+)"', html)


def expand_patterns(base_url: str, directory: str, patterns: list[str]) -> list[str]:
    full_dir_url = base_url + directory
    files = list_remote_files(full_dir_url)

    matched = []
    for pattern in patterns:
        matched.extend(
            f"{full_dir_url}{fname}" for fname in files if fnmatch(fname, pattern)
        )

    return matched
