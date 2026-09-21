FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends xrdp xorgxrdp xfce4 xterm dbus-x11 && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash fixture \
    && echo 'fixture:fixture-password' | chpasswd \
    && adduser fixture ssl-cert \
    && printf 'startxfce4\n' > /home/fixture/.xsession \
    && chown fixture:fixture /home/fixture/.xsession
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 3389
ENTRYPOINT ["/entrypoint.sh"]
