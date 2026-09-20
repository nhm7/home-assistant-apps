FROM guacamole/guacd:1.6.0 AS guacd
FROM guacamole/guacamole:1.6.0
USER root
ARG GUACAMOLE_VERSION=1.6.0
COPY --from=guacd /opt/guacamole /opt/guacamole
RUN apt-get update && apt-get install -y --no-install-recommends curl openssl python3 python3-aiohttp && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/guacamole/extensions \
    && curl -fsSL "https://downloads.apache.org/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-auth-json-${GUACAMOLE_VERSION}.tar.gz" | tar -xz -C /tmp \
    && find /tmp -type f -name "guacamole-auth-json-*.jar" -exec mv {} /etc/guacamole/extensions/ \;
COPY run.sh /run.sh
COPY gateway.py /gateway.py
RUN chmod +x /run.sh
CMD ["/run.sh"]
