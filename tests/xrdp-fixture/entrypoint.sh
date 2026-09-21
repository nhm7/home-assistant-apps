#!/bin/sh
set -eu
mkdir -p /run/xrdp
rm -f /run/xrdp/xrdp.pid /run/xrdp/xrdp-sesman.pid
xrdp-sesman --nodaemon &
sesman_pid=$!
xrdp --nodaemon &
xrdp_pid=$!
trap 'kill "$xrdp_pid" "$sesman_pid" 2>/dev/null || true' INT TERM EXIT
wait "$xrdp_pid"
