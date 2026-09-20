# RDP Gateway App

This app bundles Apache Guacamole as an HTML5 RDP gateway. Access is provided
through the companion `rdp_gateway` custom integration, which checks Home
Assistant user permissions before issuing a session.

## Security

- `rdp_password` and `gateway_secret` are password fields. Never expose them
  in logs, commits, or URLs.
- The `gateway_secret` must be identical in the app and integration settings.
- Permit RDP port 3389 only between the app and target machine; never expose it
  directly to the internet.
- The integration panel enforces `admins_only` server-side.

The app generates Guacamole's RDP connection configuration at startup and uses
a short-lived signed session issued by Home Assistant.
