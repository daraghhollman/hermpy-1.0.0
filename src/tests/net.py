import unittest
from unittest import TestCase

from hermpy.net import ClientMESSENGER


class TestInstruments(TestCase):

    def test_messenger_instruments(self):

        client = ClientMESSENGER()

        mag_items = ["MAG", "MAG 1s", "MAG 5s", "MAG 10s", "MAG 60s"]
        has_mag = all([item in client.FILE_PATTERN.keys() for item in mag_items])
        self.assertTrue(has_mag)

        fips_items = ["FIPS"]
        has_fips = all([item in client.FILE_PATTERN.keys() for item in fips_items])
        self.assertTrue(has_fips)


if __name__ == "__main__":
    unittest.main()
