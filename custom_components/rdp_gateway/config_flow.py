from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_ADMINS_ONLY, CONF_GATEWAY_SECRET, CONF_INGRESS_PATH, DEFAULT_ADMINS_ONLY, DOMAIN


class RdpGatewayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="RDP Gateway", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_INGRESS_PATH, default="/api/hassio_ingress/rdp_gateway"): str,
                vol.Required(CONF_GATEWAY_SECRET): str,
                vol.Required(CONF_ADMINS_ONLY, default=DEFAULT_ADMINS_ONLY): bool,
            }),
        )
