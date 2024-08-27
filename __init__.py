"""__init__.py."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SNMP integration from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True
