"""
A minimal example of how the network clients can be used to download and load data
"""

from sunpy.time import TimeRange

from hermpy.net import ClientMESSENGER

# We initialise a client for the MESSENGER mission. The sources
# are set by defaults in src/hermpy/net/client_messenger.py, but
# can be changed in the class constructor.
client = ClientMESSENGER()

# Available intruments in the client can be listed:
print(client.instruments)

# A query can be made for any range of time using Sunpy's TimeRange as
# an input. The instrument ("MAG" in this example) must also be passed
# to the client. The instrument must exist in the client source.
query = client.query(TimeRange("2011-06-01", "2011-06-02"), "MAG")

# The client returns a list of urls, which can be checked before downloading.
# These are automatically added to the query buffer
# (ClientMESSENGER._query_buffer: list[str]). These calls extend a list of
# queries, and so multiple queries can be made before downloading. This is
# useful for accessing multiple instruments, or non-continous timespans.
print(query)

# We can access files added to the query buffer with this function. They will
# be downloaded if not already in cache, and their path returned. The query
# buffer is automatically flushed after this call.
# Redownloads can be forced with check_for_updates=True
local_paths = client.fetch()

print(local_paths)
