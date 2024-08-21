import re

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

IPV4_REGEX = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"


@config_entries.HANDLERS.register(DOMAIN)
class SnmpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SNMP."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow handler."""
        return SnmpOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            ip_address = user_input.get(CONF_IP_ADDRESS, "")

            # 验证 IP 地址是否符合 0-255.0-255.0-255.0-255 的格式
            if not re.match(IPV4_REGEX, ip_address):
                errors[CONF_IP_ADDRESS] = "Invalid IP address"
            else:
                # 进一步检查每个部分是否在 0-255 之间
                octets = ip_address.split(".")
                if any(not (0 <= int(octet) <= 255) for octet in octets):
                    errors[CONF_IP_ADDRESS] = "Invalid IP address"

            update_interval = user_input.get("update_interval", 30)
            try:
                update_interval = int(update_interval)
                if update_interval < 20 or update_interval > 300:
                    errors["update_interval"] = "Invalid update interval"
            except ValueError:
                errors["update_interval"] = "Invalid update interval"

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        # Define the form schema with update_interval
        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): cv.string,
                vol.Required(CONF_IP_ADDRESS): cv.string,
                vol.Required("community"): cv.string,
                vol.Optional("update_interval", default=30): vol.Coerce(int),
            }
        )

        # Use description_placeholders to show the hints
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "name": "Enter the name of the device.",
                "ip_address": "Enter the IP address of the device, e.g., 192.168.1.1.",
                "community": "Enter the SNMP community string. The default is 'public'.",
                "update_interval": "Enter the update interval (20-300 seconds).",
            },
        )


class SnmpOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle SNMP options."""

    def __init__(self, config_entry):
        """Initialize SNMP options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initial step of the options flow."""
        errors = {}

        if user_input is not None:
            update_interval = user_input.get("update_interval", 30)
            try:
                update_interval = int(update_interval)
                if update_interval < 20 or update_interval > 300:
                    errors["update_interval"] = "Invalid update interval"
            except ValueError:
                errors["update_interval"] = "Invalid update interval"

            if not errors:
                return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {vol.Optional("update_interval", default=30): vol.Coerce(int)}
        )

        return self.async_show_form(
            step_id="init", data_schema=data_schema, errors=errors
        )
