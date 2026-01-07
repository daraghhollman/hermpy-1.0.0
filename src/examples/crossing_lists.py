import os
from pathlib import Path

import requests

from hermpy.data import CrossingList

EXAMPLES_DATA_DIR = Path(__file__).parent / "example-data/"

# Ensure directory exists, if not, create it.
if not os.path.isdir(EXAMPLES_DATA_DIR):
    os.makedirs(EXAMPLES_DATA_DIR)

# Download a crossing list
url = "https://zenodo.org/records/17814795/files/hollman_2025_crossing_list.csv?download=1"
local_csv_path = EXAMPLES_DATA_DIR / "hollman_2025_crossing_list.csv"

response = requests.get(url)
with open(local_csv_path, "wb") as file:
    file.write(response.content)

# Make a new crossing list from csv file
crossings = CrossingList.from_csv(local_csv_path, time_column="Time")

print(crossings.table)
