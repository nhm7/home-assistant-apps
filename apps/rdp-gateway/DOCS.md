# RDP Gateway

RDP Gateway adds a browser-based RDP session to Home Assistant through the
Ingress panel. It connects to one Windows or Linux RDP server using Apache
Guacamole.

## Configuration

Open the app configuration and enter the RDP server address, port, username,
and password. The default port is `3389`. Set a Windows domain only when the
server requires one.

`Any` lets the server and client negotiate a compatible protocol. `NLA`, `TLS`,
and `RDP` force a particular protocol and are useful when the server requires
one.

Keep certificate validation enabled whenever possible. `Ignore the RDP
certificate` disables that validation and should only be enabled for a trusted
server whose certificate cannot be validated.

Keep the RDP server reachable only from the Home Assistant network or app;
do not expose its port directly to the internet. The app panel is restricted
to Home Assistant administrators.

After saving the configuration, open the app from the Home Assistant sidebar.

## Troubleshooting

If the app itself does not start, check the app log for startup or Guacamole
errors. If the app starts but the session cannot connect, verify that the
configured host and port are reachable from the Home Assistant machine, that
the credentials are valid, and that the RDP server accepts the selected
security mode. Changing certificate validation will not fix a refused TCP
connection.
