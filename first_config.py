from jnpr.junos import Device
from jnpr.junos.utils.config import Config

# Device connection info
dev = Device(
    host="192.168.90.182",
    user="ericzet",
    password="Tagg!s123!#%9"
)

dev.open()
cu = Config(dev)

# Build the configuration
config_snippet = """
set interfaces ge-0/0/5 description "eric test"
set interfaces ge-0/0/5 unit 0 family inet address 1.1.1.1/30

set routing-instances ERIC-VRF instance-type vrf
set routing-instances ERIC-VRF interface ge-0/0/5.0
set routing-instances ERIC-VRF route-distinguisher 65000:1
set routing-instances ERIC-VRF vrf-target target:65000:1
"""

# Load and commit
cu.load(config_snippet, format="set")
cu.commit()

print("Configuration applied successfully.")

dev.close()
