"""sensor.py."""

from datetime import timedelta
import logging

from pysnmp.hlapi.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    getCmd,
)
from pysnmp.proto import rfc1902

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, OIDS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SNMP sensors."""
    update_interval = config_entry.data.get(
        "update_interval", 30
    )  # 取得使用者輸入的更新間隔
    coordinator = SnmpDataUpdateCoordinator(hass, config_entry.data, update_interval)
    await coordinator.async_config_entry_first_refresh()

    sensors = []
    for oid, description in OIDS.items():
        sensors.append(SnmpSensor(coordinator, config_entry, oid, description))

    async_add_entities(sensors)


class SnmpDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching SNMP data."""

    def __init__(self, hass, config, update_interval):
        """Initialize."""
        self._ip = config[CONF_IP_ADDRESS]
        self._community = config.get("community", "public")
        super().__init__(
            hass,
            _LOGGER,
            name="SNMP data",
            update_interval=timedelta(seconds=update_interval),  # 使用者設定的更新間隔
        )

    async def _async_update_data(self):
        """Fetch data from SNMP."""
        return await fetch_snmp_data(self._ip, self._community, OIDS)


async def fetch_snmp_data(target_ip, community_string, oids):
    """Fetch SNMP data asynchronously."""
    result = {}
    for oid, description in oids.items():
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(community_string),
            UdpTransportTarget((target_ip, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )
        if errorIndication or errorStatus:
            result[description] = "Error"
        else:
            for varBind in varBinds:
                # 处理 system uptime
                if oid == "1.3.6.1.2.1.1.3.0":
                    uptime = varBind[1]
                    if isinstance(uptime, rfc1902.TimeTicks):
                        uptime_seconds = int(uptime) / 100  # TimeTicks 是百分之一秒
                        days, remainder = divmod(uptime_seconds, 86400)
                        hours, remainder = divmod(remainder, 3600)
                        minutes, seconds = divmod(remainder, 60)

                        formatted_uptime = []
                        if days > 0:
                            formatted_uptime.append(f"{int(days)}d")
                        if hours > 0 or days > 0:
                            formatted_uptime.append(f"{int(hours)}h")
                        if minutes > 0 or hours > 0 or days > 0:
                            formatted_uptime.append(f"{int(minutes)}m")
                        formatted_uptime.append(f"{int(seconds)}s")

                        formatted_uptime_str = " ".join(formatted_uptime)
                        result[description] = formatted_uptime_str
                    else:
                        result[description] = varBind[1].prettyPrint()
                elif oid in [
                    "1.3.6.1.4.1.890.1.15.3.2.4.0",
                    "1.3.6.1.4.1.890.1.15.3.2.5.0",
                ]:
                    result[description] = f"{varBind[1].prettyPrint()}%"
                else:
                    result[description] = varBind[1].prettyPrint()
    return result


class SnmpSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SNMP Sensor."""

    def __init__(self, coordinator, config_entry, oid, description):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = f"{config_entry.data[CONF_NAME]} {description}"
        self._oid = oid
        self._description = description
        self._config_entry = config_entry
        self._icon = self._determine_icon()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._description)

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._config_entry.entry_id}_{self._oid}"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    def _determine_icon(self):
        """Determine the icon based on OID or description."""
        if "model" in self._description.lower():  # model
            return "mdi:database-outline"
        elif "version" in self._description.lower():  # version
            return "mdi:alpha-v-box-outline"
        elif "serial number" in self._description.lower():  # serial-number
            return "mdi:format-list-numbered-rtl"
        elif "country" in self._description.lower():  # country
            return "mdi:map-marker-circle"
        elif "uptime" in self._description.lower():  # uptime
            return "mdi:clock-time-eight-outline"
        elif "cpu" in self._description.lower():  # cpu
            return "mdi:chip"
        elif "ram" in self._description.lower():  # ram
            return "mdi:memory"
        elif (
            "2.4ghz current channel" in self._description.lower()
            or "5ghz current channel" in self._description.lower()
        ):  # 2.4g
            return "mdi:radio-tower"
        else:
            return "mdi:transit-connection-variant"

    @property
    def device_info(self):
        """Return device information to group entities under a single device."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "name": self._config_entry.data[CONF_NAME],
            "model": "SNMP Monitor Device",
            "manufacturer": "Zyxel Network",
        }
