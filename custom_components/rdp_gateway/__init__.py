"""Home Assistant authorization boundary for the RDP Gateway app."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components import websocket_api

from .const import DOMAIN
from .panel import async_register_panel
from .panel import ws_create_session


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Register the panel. Authorization happens on every session request."""
    await async_register_panel(hass, entry)
    websocket_api.async_register_command(hass, ws_create_session)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True
