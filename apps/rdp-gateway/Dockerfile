FROM debian:bookworm-slim
ARG GUACAMOLE_VERSION=1.6.0
RUN apt-get update && apt-get install -y --no-install-recommends curl guacamole-server python3 python3-aiohttp tomcat10 && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL "https://downloads.apache.org/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-${GUACAMOLE_VERSION}.war" -o /var/lib/tomcat10/webapps/guacamole.war \
    && mkdir -p /etc/guacamole/extensions \
    && curl -fsSL "https://downloads.apache.org/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-auth-header-${GUACAMOLE_VERSION}.tar.gz" | tar -xz -C /tmp \
    && mv /tmp/guacamole-auth-header-${GUACAMOLE_VERSION}.jar /etc/guacamole/extensions/
COPY run.sh /run.sh
COPY gateway.py /gateway.py
RUN chmod +x /run.sh
CMD ["/run.sh"]
