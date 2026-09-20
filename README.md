# Home Assistant Apps

Eine Sammlung eigenständiger Home-Assistant-Apps und zugehöriger Custom
Integrations. Jede App lebt in einem eigenen Verzeichnis unter `apps/`
und kann unabhängig versioniert und veröffentlicht werden.

## Enthaltene Apps

| App | Zweck |
| --- | --- |
| [`rdp-gateway`](apps/rdp-gateway) | Browser-basierter, in Home Assistant eingebetteter RDP-Zugriff |

Die optionale Custom Integration liegt unter `custom_components/rdp_gateway`.
Sie wird den Sidebar-Eintrag und die Zugriffsregel auf Basis des angemeldeten
Home-Assistant-Nutzers bereitstellen.
