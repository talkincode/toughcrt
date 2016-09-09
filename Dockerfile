FROM daocloud.io/toughcloud/docker-base
MAINTAINER toughcloud <support@toughstruct.com>

VOLUME [ "/var/toughcrt" ]


RUN git clone -b master https://git.coding.net/toughstruct/toughcrt.git /opt/toughcrt && \
    ln -s /opt/toughcrt/etc/toughcrt.json /etc/toughcrt.json

RUN pip install -U --no-deps https://github.com/talkincode/txweb/archive/master.zip
RUN pip install click psutil

ADD entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh


ADD install.sh /install.sh 
RUN sh /install.sh

EXPOSE 8080
EXPOSE 3799/udp
EXPOSE 2000/udp

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["txwebctl  --conf=/etc/toughcrt.json --dir=/opt/toughcrt/toughcrt --logging=none"]
