# RDP Gateway App

This app bundles Apache Guacamole as an HTML5 RDP gateway.

## Security

- `rdp_password` is a password field. Never expose it
  in logs, commits, or URLs.
- Permit RDP port 3389 only between the app and target machine; never expose it
  directly to the internet.
- By default, the sidebar panel is restricted to Home Assistant administrators.
  Set `panel_admin: false` in `config.yaml` only when every signed-in user
  should be allowed to open it.

The app generates Guacamole's RDP connection configuration at startup. Home
Assistant Ingress authenticates users before requests reach the app.
