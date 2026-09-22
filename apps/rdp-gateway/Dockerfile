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
CMD ["/run.sh"]
ENTRYPOINT []
