#!/bin/sh
set -eu
python3 /gateway.py --configure
export GUACAMOLE_HOME=/etc/guacamole
export LD_LIBRARY_PATH=/opt/guacamole/lib
/opt/guacamole/sbin/guacd -b 127.0.0.1 -p 4822 &
/opt/guacamole/bin/entrypoint.sh &
exec python3 /gateway.py
