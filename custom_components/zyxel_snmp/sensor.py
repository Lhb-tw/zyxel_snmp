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

from .const import DOMAIN, OIDS_AP, OIDS_SWITCH

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SNMP sensors."""
    user_update_interval = config_entry.data.get("update_interval", 30)
    device_type = config_entry.data.get("device_type")

    # 根据设备类型选择对应的 OID 集
    oids = OIDS_AP if device_type == "Access Point" else OIDS_SWITCH

    # 调整更新间隔以补偿延迟
    adjusted_update_interval = max(5, user_update_interval - 5)

    # 获取端口数量
    port_quantity_oid = "1.3.6.1.2.1.2.1.0"
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(config_entry.data.get("community", "public")),
        UdpTransportTarget((config_entry.data[CONF_IP_ADDRESS], 161)),
        ContextData(),
        ObjectType(ObjectIdentity(port_quantity_oid)),
    )

    if errorIndication or errorStatus:
        port_quantity = 0
    else:
        port_quantity = int(varBinds[0][1])

    coordinator = SnmpDataUpdateCoordinator(
        hass, config_entry.data, adjusted_update_interval, oids, port_quantity
    )
    await coordinator.async_config_entry_first_refresh()

    sensors = []

    # 为 AP 设备创建传感器
    if device_type == "Access Point":
        sensors.extend(
            SnmpSensor(coordinator, config_entry, oid, description)
            for oid, description in oids.items()
        )

    # 为 Switch 设备创建传感器
    elif device_type == "Switch":
        # 添加常规 OID 传感器
        for oid, description in oids.items():
            if description not in ["Port Status", "Port PoE"]:
                sensors.append(SnmpSensor(coordinator, config_entry, oid, description))

        # 动态创建端口相关的传感器
        for i in range(1, port_quantity + 1):
            port_status_oid = f"1.3.6.1.4.1.890.1.15.3.61.2.1.1.2.{i}"
            sensors.append(
                SnmpSensor(
                    coordinator, config_entry, port_status_oid, f"Port {i} status"
                )
            )

            poe_status_oid = f"1.3.6.1.4.1.890.1.15.3.59.2.1.1.1.{i}"
            sensors.append(
                SnmpSensor(coordinator, config_entry, poe_status_oid, f"Port {i} PoE")
            )

    async_add_entities(sensors)


class SnmpDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching SNMP data."""

    def __init__(self, hass, config, update_interval, oids, port_quantity):
        """Initialize."""
        self._ip = config[CONF_IP_ADDRESS]
        self._community = config.get("community", "public")
        self._oids = oids
        self._port_quantity = port_quantity
        super().__init__(
            hass,
            _LOGGER,
            name="SNMP data",
            update_interval=timedelta(seconds=update_interval),  # 使用者設定的更新間隔
        )

    async def _async_update_data(self):
        """Fetch data from SNMP."""
        return await fetch_snmp_data(
            self._ip, self._community, self._oids, self._port_quantity
        )


async def fetch_snmp_data(target_ip, community_string, oids, port_quantity):
    """Fetch SNMP data asynchronously."""
    result = {}

    for oid, description in oids.items():
        if oid == "1.3.6.1.4.1.890.1.15.3.61.2.1.1.2":  # Port Status OID
            for i in range(1, port_quantity + 1):
                port_status_oid = f"{oid}.{i}"
                errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                    SnmpEngine(),
                    CommunityData(community_string),
                    UdpTransportTarget((target_ip, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(port_status_oid)),
                )

                if errorIndication or errorStatus:
                    result[f"Port {i} status"] = "Error"
                else:
                    status_value = varBinds[0][1].prettyPrint()
                    if "No Such Instance" in status_value:
                        result[f"Port {i} status"] = "Not Support"
                    elif status_value == "1":
                        result[f"Port {i} status"] = "Up"
                    else:
                        result[f"Port {i} status"] = "Down"

        elif oid == "1.3.6.1.4.1.890.1.15.3.59.2.1.1.1":  # Port PoE Status OID
            for i in range(1, port_quantity + 1):
                port_poe_status_oid = f"{oid}.{i}"
                errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                    SnmpEngine(),
                    CommunityData(community_string),
                    UdpTransportTarget((target_ip, 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(port_poe_status_oid)),
                )

                if errorIndication or errorStatus:
                    result[f"Port {i} PoE"] = "Error"
                else:
                    poe_status_value = varBinds[0][1].prettyPrint()
                    if "No Such Instance" in poe_status_value:
                        result[f"Port {i} PoE"] = "Not Support"
                    else:
                        poe_status_float = float(poe_status_value) / 1000
                        if poe_status_float == 0:
                            result[f"Port {i} PoE"] = "0 Watt"
                        else:
                            result[f"Port {i} PoE"] = f"{poe_status_float:.1f} Watt"

        elif oid == "1.3.6.1.4.1.890.1.15.3.1.6.0":  # Firmware Version OID
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
                value = varBinds[0][1].prettyPrint()
                if "No Such Instance" in value:
                    result[description] = "Not Support"
                else:
                    # 正规化 Firmware Version 的格式，只保留 | 之前的部分
                    if "|" in value:
                        value = value.split("|")[0].strip()
                    result[description] = value

        elif oid in [
            "1.3.6.1.4.1.890.1.15.3.2.4.0",
            "1.3.6.1.4.1.890.1.15.3.2.5.0",
        ]:  # CPU and RAM OIDs
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
                value = varBinds[0][1].prettyPrint()
                if "No Such Instance" in value:
                    result[description] = "Not Support"
                else:
                    # 添加 "%" 符号
                    result[description] = value

        else:
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
                value = varBinds[0][1].prettyPrint()
                if "No Such Instance" in value:
                    result[description] = "Not Support"
                elif oid == "1.3.6.1.2.1.1.3.0":  # System Uptime OID
                    uptime = varBinds[0][1]
                    if isinstance(uptime, rfc1902.TimeTicks):
                        uptime_seconds = (
                            int(uptime) / 100
                        )  # TimeTicks 是以百分之一秒为单位
                        days, remainder = divmod(uptime_seconds, 86400)  # 86400秒 = 1天
                        hours, remainder = divmod(remainder, 3600)  # 3600秒 = 1小时
                        minutes, seconds = divmod(remainder, 60)  # 60秒 = 1分钟

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
                        result[description] = uptime.prettyPrint()
                else:
                    result[description] = value

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
        desc = self._description.lower()
        if "model" in desc:
            return "mdi:database-outline"
        elif "version" in desc:
            return "mdi:alpha-v-box-outline"
        elif "serial number" in desc:
            return "mdi:format-list-numbered-rtl"
        elif "country" in desc:
            return "mdi:map-marker-circle"
        elif "uptime" in desc:
            return "mdi:clock-time-eight-outline"
        elif "cpu" in desc:
            return "mdi:chip"
        elif "ram" in desc:
            return "mdi:memory"
        elif "port" in desc and "status" in desc:  # Port Status
            return "mdi:ethernet"
        elif "poe" in desc:  # Port PoE Status
            return "mdi:power-settings"
        elif "2.4ghz current channel" in desc or "5ghz current channel" in desc:
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
