from jnpr.junos import Device

# Replace with your device info
dev = Device(host='192.168.90.182', user='ericzet', password='Tagg!s123!#%9')

dev.open()

print("Connected to:", dev.facts.get('hostname'))
print("Model:", dev.facts.get('model'))
print("Serial:", dev.facts.get('serialnumber'))
print("Version:", dev.facts.get('version'))
print("Uptime:", dev.facts.get('RE0', {}).get('up_time'))

dev.close()
