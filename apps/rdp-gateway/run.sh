#!/bin/sh
set -eu
python3 /gateway.py --configure
export GUACAMOLE_HOME=/etc/guacamole
guacd -b 127.0.0.1 -p 4822 &
CATALINA_BASE=/var/lib/tomcat10 CATALINA_HOME=/usr/share/tomcat10 /usr/libexec/tomcat10/tomcat-start.sh
exec python3 /gateway.py
