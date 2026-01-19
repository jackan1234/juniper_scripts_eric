from jnpr.junos import Device
from jnpr.junos.utils.config import Config

# Device connection info
dev = Device(
    host="192.168.90.183",
    user="ericzet",
    password="Tagg!s123!#%9"
)

dev.open()
cu = Config(dev)

# Build the configuration
config_snippet = """
set interfaces ae1 unit 105 description 105
set interfaces ae1 unit 105 encapsulation vlan-bridge
set interfaces ae1 unit 105 vlan-id 105
set interfaces irb unit 105 family inet address 10.20.105.254/24
set interfaces irb unit 105 mac 00:00:5e:00:53:ad

set routing-instances 105_evpn instance-type mac-vrf
set routing-instances 105_evpn protocols evpn encapsulation vxlan
set routing-instances 105_evpn protocols evpn default-gateway no-gateway-community
set routing-instances 105_evpn protocols evpn extended-vni-list 50105
set routing-instances 105_evpn vtep-source-interface lo0.0
set routing-instances 105_evpn bridge-domains bd-105 vlan-id 105
set routing-instances 105_evpn bridge-domains bd-105 interface ae1.105
set routing-instances 105_evpn bridge-domains bd-105 routing-interface irb.105
set routing-instances 105_evpn bridge-domains bd-105 vxlan vni 50105
set routing-instances 105_evpn service-type vlan-aware
set routing-instances 105_evpn route-distinguisher 2.2.2.2:555
set routing-instances 105_evpn vrf-target target:65000:5555

set routing-instances vrf_test_105 instance-type vrf
set routing-instances vrf_test_105 routing-options static route 0.0.0.0/0 discard
set routing-instances vrf_test_105 protocols evpn ip-prefix-routes advertise direct-nexthop
set routing-instances vrf_test_105 protocols evpn ip-prefix-routes encapsulation vxlan
set routing-instances vrf_test_105 protocols evpn ip-prefix-routes vni 50998
set routing-instances vrf_test_105 protocols evpn ip-prefix-routes export EVPN-TYPE5-EXPORT
set routing-instances vrf_test_105 interface irb.105
set routing-instances vrf_test_105 interface lo0.105
set routing-instances vrf_test_105 route-distinguisher 10:105
set routing-instances vrf_test_105 vrf-target target:10:105
set routing-instances vrf_test_105 vrf-table-label
set policy-options policy-statement EVPN-TYPE5-EXPORT term VLAN104 from protocol direct
set policy-options policy-statement EVPN-TYPE5-EXPORT term VLAN104 from route-filter 10.10.104.0/24 exact
set policy-options policy-statement EVPN-TYPE5-EXPORT term VLAN104 from route-filter 10.20.105.0/24 exact
set policy-options policy-statement EVPN-TYPE5-EXPORT term VLAN104 from route-filter 10.10.105.0/24 exact
set policy-options policy-statement EVPN-TYPE5-EXPORT term VLAN104 then accept
"""

# Load and commit
cu.load(config_snippet, format="set")
cu.commit()

print("Configuration applied successfully.")

dev.close()
