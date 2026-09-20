FROM guacamole/guacamole:1.6.0 AS client
FROM guacamole/guacd:1.6.0
USER root
ARG GUACAMOLE_VERSION=1.6.0
ARG TOMCAT_VERSION=9.0.106
RUN apk add --no-cache curl openssl openjdk17-jre py3-aiohttp python3 tar \
    && curl -fsSL "https://archive.apache.org/dist/tomcat/tomcat-9/v${TOMCAT_VERSION}/bin/apache-tomcat-${TOMCAT_VERSION}.tar.gz" | tar -xz -C /opt \
    && mv "/opt/apache-tomcat-${TOMCAT_VERSION}" /opt/tomcat \
    && mkdir -p /etc/guacamole/extensions \
    && curl -fsSL "https://downloads.apache.org/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-auth-json-${GUACAMOLE_VERSION}.tar.gz" | tar -xz -C /tmp \
    && find /tmp -type f -name "guacamole-auth-json-*.jar" -exec mv {} /etc/guacamole/extensions/ \;
COPY --from=client /opt/guacamole/webapp/guacamole.war /opt/tomcat/webapps/guacamole.war
COPY run.sh /run.sh
COPY gateway.py /gateway.py
RUN chmod +x /run.sh
CMD ["/run.sh"]
