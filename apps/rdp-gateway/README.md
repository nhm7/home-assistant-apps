# RDP Gateway App

Diese App bündelt Apache Guacamole als HTML5-RDP-Gateway. Sie wird nicht
direkt veröffentlicht: Der Zugriff erfolgt über die mitgelieferte
`rdp_gateway`-Custom-Integration, welche die Home-Assistant-Nutzerrechte vor
dem Ausstellen einer Sitzung prüft.

## Sicherheit

- `rdp_password` und `gateway_secret` sind Passwortfelder und dürfen nie in
  Logs, Commits oder URLs erscheinen.
- Der `gateway_secret` muss identisch in App und Integration hinterlegt sein.
- RDP-Port 3389 nur zwischen App und Zielmaschine freischalten – niemals
  ins Internet weiterleiten.
- Das App-Panel bleibt administrativ verborgen. Die normale Nutzung erfolgt
  über das Integration-Panel, das `admins_only` serverseitig durchsetzt.

Die Laufzeit-Konfiguration von Guacamole und die signierte Sitzungsübergabe
sind in dieser ersten Struktur bewusst noch nicht aktiviert; ohne diese beiden
Bausteine darf die App nicht produktiv installiert werden.
