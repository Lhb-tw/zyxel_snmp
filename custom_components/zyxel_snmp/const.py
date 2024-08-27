"""const.py."""

DOMAIN = "zyxel_snmp"

# 定义设备类型
DEVICE_TYPES = ["Access Point", "Switch"]

# 定义 AP OID 和描述
OIDS_AP = {
    "1.3.6.1.4.1.890.1.15.3.1.11.0": "Product model",
    "1.3.6.1.4.1.890.1.15.3.1.6.0": "Firmware version",
    "1.3.6.1.4.1.890.1.15.3.1.12.0": "Serial Number",
    "1.3.6.1.4.1.890.1.15.3.1.16.0": "Country code",
    "1.3.6.1.2.1.1.3.0": "System uptime",
    "1.3.6.1.4.1.890.1.15.3.2.4.0": "CPU",
    "1.3.6.1.4.1.890.1.15.3.2.5.0": "RAM",
    "1.3.6.1.4.1.890.1.15.3.5.1.1.1.1": "2.4GHz Current Channel",
    "1.3.6.1.4.1.890.1.15.3.5.1.1.1.2": "5GHz Current Channel",
    "1.3.6.1.4.1.890.1.15.3.5.15.0": "Connected Stations",
}

# 定义 Switch OID 和描述
OIDS_SWITCH = {
    "1.3.6.1.4.1.890.1.15.3.1.11.0": "Product model",
    "1.3.6.1.4.1.890.1.15.3.1.6.0": "Firmware version",
    "1.3.6.1.4.1.890.1.15.3.82.2.10.0": "Serial Number",
    "1.3.6.1.4.1.890.1.15.3.1.16.0": "Country code",
    "1.3.6.1.2.1.1.3.0": "System uptime",
    "1.3.6.1.4.1.890.1.15.3.2.4.0": "CPU",
    "1.3.6.1.4.1.890.1.15.3.2.5.0": "RAM",
    "1.3.6.1.4.1.890.1.15.3.61.2.1.1.2": "Port Status",
    "1.3.6.1.4.1.890.1.15.3.59.2.1.1.1": "Port PoE",
}
