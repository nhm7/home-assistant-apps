#!/bin/bash
set -eu
python3 /gateway.py --configure
export GUACAMOLE_HOME=/etc/guacamole
/opt/guacamole/sbin/guacd -f -b 127.0.0.1 -p 4822 &
guacd_pid=$!
export CATALINA_BASE=/opt/tomcat
export CATALINA_HOME=/opt/tomcat
/opt/tomcat/bin/catalina.sh run &
tomcat_pid=$!
gateway_pid=
trap 'kill "$guacd_pid" "$tomcat_pid" ${gateway_pid:+"$gateway_pid"} 2>/dev/null || true; wait || true' EXIT
trap 'exit 0' TERM INT
ready=false
for attempt in {1..90}; do
    kill -0 "$guacd_pid" "$tomcat_pid" || exit 1
    if curl --silent --fail http://127.0.0.1:8080/guacamole/ >/dev/null; then
        ready=true
        break
    fi
    sleep 1
done
if [ "$ready" != true ]; then
    echo 'Guacamole did not become ready within 90 seconds' >&2
    exit 1
fi
python3 /gateway.py &
gateway_pid=$!
wait -n "$guacd_pid" "$tomcat_pid" "$gateway_pid"
exit 1
