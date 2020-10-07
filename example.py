from pprint import pprint

from pynso import NSOClient

# Setup a client
client = NSOClient("10.159.91.14", "admin", "admin")

# Get information about the API
print("Getting API version number")
pprint(client.info()["yang-library-version"])

# Get the information about the running datastore
print("Getting the contents of the running datastore")
pprint(client.get_datastore("running"))

# Get a data path
print("Getting a specific data path: snmp:snmp namespace and the agent data object")
pprint(client.get_data(("snmp:snmp", "agent")))
