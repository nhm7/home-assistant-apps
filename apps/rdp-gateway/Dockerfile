FROM guacamole/guacamole:1.6.0 AS client
FROM guacamole/guacd:1.6.0
USER root
ARG BUILD_VERSION
ARG BUILD_ARCH
ARG GUACAMOLE_VERSION=1.6.0
ARG TOMCAT_VERSION=9.0.106
LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.name="RDP Gateway" \
    io.hass.description="Browser-based RDP access through Apache Guacamole" \
    org.opencontainers.image.source="https://github.com/nhm7/home-assistant-apps" \
    org.opencontainers.image.licenses="MIT"
RUN apk add --no-cache bash curl openssl openjdk17-jre py3-aiohttp python3 tar \
    && curl -fsSL "https://archive.apache.org/dist/tomcat/tomcat-9/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz" | tar -xz -C /opt \
    && mv "/opt/apache-tomcat-${TOMCAT_VERSION}" /opt/tomcat \
    && mkdir -p /etc/guacamole/extensions \
    && curl -fsSL "https://downloads.apache.org/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-auth-json-${GUACAMOLE_VERSION}.tar.gz" | tar -xz -C /tmp \
    && find /tmp -type f -name "guacamole-auth-json-*.jar" -exec mv {} /etc/guacamole/extensions/ \;
COPY --from=client /opt/guacamole/webapp/guacamole.war /opt/tomcat/webapps/guacamole.war
COPY run.sh /run.sh
COPY gateway.py /gateway.py
COPY rdp_config.py /rdp_config.py
RUN chmod +x /run.sh
# The guacd base image checks every five minutes.  Supervisor waits for a
# healthy app before exposing ingress, so that inherited interval makes a
# freshly started app appear unavailable for up to five minutes.
HEALTHCHECK --interval=5s --timeout=5s --start-period=10s --retries=12 CMD nc -z 127.0.0.1 4822 && curl --silent --fail --max-time 3 http://127.0.0.1:8081/ >/dev/null || exit 1
CMD ["/run.sh"]
ENTRYPOINT []
