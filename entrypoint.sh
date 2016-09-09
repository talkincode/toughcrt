#!/bin/sh

if [ ! -f "/var/toughcrt/data" ];then
    mkdir -p /var/toughcrt/data
fi

cd /opt/toughcrt && git pull origin master

exec "$@"