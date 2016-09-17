#!/bin/sh

pip install -U --no-deps https://github.com/talkincode/txweb/archive/master.zip
pip install -U --no-deps https://github.com/talkincode/txradius/archive/master.zip

git clone -b master https://git.coding.net/toughstruct/toughcrt.git /opt/toughcrt 

test -f /etc/toughcrt.json || cp /opt/toughcrt/etc/toughcrt.json /etc/toughcrt.json
