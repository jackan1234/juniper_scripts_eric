import yaml
from jnpr.junos import Device
from jnpr.junos.utils.config import Config

# -----------------------------
# Load inventory
# -----------------------------
with open("inventory.yaml") as f:
    inventory = yaml.safe_load(f)["devices"]


# -----------------------------
# Helper: filter by role
# -----------------------------
def filter_by_role(inventory, role):
    return [dev for dev in inventory if dev.get("role") == role]


# -----------------------------
# Helper: show numbered list
# -----------------------------
def show_device_list(devices):
    print("\nAvailable devices:")
    for i, dev in enumerate(devices, start=1):
        print(f"{i}. {dev['name']} ({dev['host']})")


# -----------------------------
# Helper: select one device
# -----------------------------
def select_single_device(devices):
    show_device_list(devices)
    choice = int(input("Select the device number to configure: "))
    if choice < 1 or choice > len(devices):
        print("Invalid selection.")
        exit()
    return devices[choice - 1]


# -----------------------------
# Helper: select multiple devices
# -----------------------------
def select_multiple_devices(devices):
    show_device_list(devices)
    selection = input("Select devices (e.g. 1,3,5 or 2-4 or all): ").strip()

    if selection.lower() == "all":
        return devices

    selected = []
    parts = selection.split(",")

    for part in parts:
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            for i in range(int(start), int(end) + 1):
                selected.append(devices[i - 1])
        else:
            selected.append(devices[int(part) - 1])

    return selected


# -----------------------------
# Selection mode
# -----------------------------
print("Selection options:")
print("1. Select ONE device")
print("2. Select MULTIPLE devices")
print("3. Select ALL devices with a specific ROLE")

mode = input("Choose selection mode: ").strip()

if mode == "1":
    devices_to_configure = [select_single_device(inventory)]

elif mode == "2":
    devices_to_configure = select_multiple_devices(inventory)

elif mode == "3":
    role = input("Enter role (e.g. core, distribution, access): ").strip()
    filtered = filter_by_role(inventory, role)

    if not filtered:
        print(f"No devices found with role '{role}'")
        exit()

    devices_to_configure = select_multiple_devices(filtered)

else:
    print("Invalid selection.")
    exit()


# -----------------------------
# FULL CONFIGURATION SNIPPET
# -----------------------------
config_snippet = """
set interfaces ae1 unit 105 description test_105
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


# -----------------------------
# Apply config
# -----------------------------
for dev_info in devices_to_configure:
    print(f"\nConnecting to {dev_info['name']} ({dev_info['host']})")

    dev = Device(
        host=dev_info["host"],
        user=dev_info["user"],
        password=dev_info["password"]
    )

    dev.open()
    cu = Config(dev)

    cu.load(config_snippet, format="set")
    cu.commit()

    print(f"Configuration applied to {dev_info['name']}")

    dev.close()
