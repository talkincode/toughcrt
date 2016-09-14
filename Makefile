install:
	(\
	virtualenv venv --relocatable;\
	test -d /data/toughcrt/data || mkdir -p /data/toughcrt/data;\
	ln -s /data/toughcrt /var/toughcrt;\
	test -f /etc/toughcrt.conf || cp etc/toughcrt.conf /etc/toughcrt.conf;\
	test -f /etc/toughcrt.json || cp etc/toughcrt.json /etc/toughcrt.json;\
	test -f /etc/init.d/toughcrt || cp etc/toughcrt /etc/init.d/toughcrt;\
	chmod +x /etc/init.d/toughcrt && chkconfig toughcrt on;\
	test -f /usr/lib/systemd/system/toughcrt.service || cp etc/toughcrt.service /usr/lib/systemd/system/toughcrt.service;\
	chmod 754 /usr/lib/systemd/system/toughcrt.service && systemctl enable toughcrt;\
	systemctl daemon-reload;\
	)

install-deps:
	(\
	yum install -y epel-release;\
	yum install -y wget zip python-devel libffi-devel openssl openssl-devel gcc git;\
	yum install -y czmq czmq-devel python-virtualenv supervisor;\
	yum install -y mysql-devel MySQL-python redis;\
	test -f /usr/local/bin/supervisord || ln -s `which supervisord` /usr/local/bin/supervisord;\
	)

venv:
	(\
	test -d venv || virtualenv venv;\
	source venv/bin/activate && pip install -U pip;\
	source venv/bin/activate && pip install -U wheel;\
	source venv/bin/activate && pip install -U Click;\
	source venv/bin/activate && pip install -U --no-deps https://github.com/talkincode/txweb/archive/master.zip;\
	source venv/bin/activate && pip install -U -r requirements.txt;\
	)


upgrade:
	(\
	git pull --rebase --stat origin master;\
	service toughcrt restart;\
	)


txweb:
	source venv/bin/activate && pip install -U --no-deps https://github.com/talkincode/txweb/archive/master.zip

initdb:
	python servctl initdb -f -c /etc/toughcrt.json

inittest:
	python servctl inittest -c /etc/toughcrt.json

clean:
	rm -fr venv

reconfig:
	(\
	rm -f /etc/toughcrt.conf && cp etc/toughcrt.conf /etc/toughcrt.conf;\
	rm -f /etc/toughcrt.json && cp etc/toughcrt.json /etc/toughcrt.json;\
	rm -f /etc/init.d/toughcrt && cp etc/toughcrt /etc/init.d/toughcrt;\
	chmod +x /etc/init.d/toughcrt && chkconfig toughcrt on;\
	rm -f /usr/lib/systemd/system/toughcrt.service && cp etc/toughcrt.service /usr/lib/systemd/system/toughcrt.service;\
	chmod 754 /usr/lib/systemd/system/toughcrt.service && systemctl enable toughcrt;\
	systemctl daemon-reload;\
	)

run:
	source venv/bin/activate && txwebctl  --conf=etc/toughcrt.json --dir=toughcrt --logging=none

lrun:
	txwebctl  --conf=etc/toughcrt.json --dir=toughcrt --logging=none

worker:
	txappctl  --app=worker --conf=etc/toughcrt.json --dir=toughcrt --logging=none

all:install-deps venv install

.PHONY: venv initdb inittest run install-deps venv txweb install



	