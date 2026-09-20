"""Panel registration and authorization helpers.

This module deliberately centralizes policy: a future signed-session API must
call ``user_may_open_session`` before issuing any token to the app.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import time
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components import panel_custom, websocket_api
from homeassistant.components.http import StaticPathConfig
import voluptuous as vol

from .const import CONF_ADMINS_ONLY


def user_may_open_session(entry: ConfigEntry, user) -> bool:
    """Return whether this authenticated HA user may start RDP."""
    return not entry.data[CONF_ADMINS_ONLY] or user.is_admin


async def async_register_panel(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register once the signed-session frontend is available.

    A panel is intentionally not registered yet: showing an app ingress URL
    before the signed-session broker exists would make the admin toggle merely
    cosmetic. This fail-closed behavior is part of the security contract.
    """
    hass.data.setdefault("rdp_gateway", {})[entry.entry_id] = entry
    await hass.http.async_register_static_paths([StaticPathConfig("/rdp_gateway_static", str(Path(__file__).parent / "frontend"), False)])
    await panel_custom.async_register_panel(hass, frontend_url_path="rdp-gateway", webcomponent_name="rdp-gateway-panel", module_url="/rdp_gateway_static/panel.js", sidebar_title="RDP Gateway", sidebar_icon="mdi:remote-desktop", require_admin=entry.data[CONF_ADMINS_ONLY])

@websocket_api.websocket_command({vol.Required("type"): "rdp_gateway/create_session"})
@websocket_api.async_response
async def ws_create_session(hass, connection, msg):
    entry = next(iter(hass.data["rdp_gateway"].values()))
    if not user_may_open_session(entry, connection.user):
        connection.send_error(msg["id"], "unauthorized", "Administrator access is required")
        return
    body = base64.urlsafe_b64encode(json.dumps({"exp": time.time() + 60}).encode()).rstrip(b"=").decode()
    signature = base64.urlsafe_b64encode(hmac.new(entry.data["gateway_secret"].encode(), body.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
    connection.send_result(msg["id"], {"url": f"{entry.data['ingress_path'].rstrip('/')}/launch?token={body}.{signature}"})
