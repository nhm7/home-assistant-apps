#!/bin/sh
set -eu
python3 /gateway.py --configure
export GUACAMOLE_HOME=/etc/guacamole
/opt/guacamole/sbin/guacd -b 127.0.0.1 -p 4822 &
export CATALINA_BASE=/opt/tomcat
export CATALINA_HOME=/opt/tomcat
/opt/tomcat/bin/catalina.sh start
exec python3 /gateway.py
