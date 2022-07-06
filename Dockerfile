FROM ubuntu:latest

ARG VERSION

#apt-get upgrade --assume-yes \ #Play with adding this at some point?  If needed...
RUN apt-get update && apt-get install -y apt-utils locales \
  && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

ENV LANG en_US.utf8

RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/ytdl-server

WORKDIR /var/ytdl-server

COPY dist/ytdl_server-${VERSION}.tar.gz /var/ytdl-server/ytdl_server.tar.gz

RUN pip install --upgrade pip \
  pip install --no-cache-dir '/var/ytdl-server/ytdl_server.tar.gz'

EXPOSE 8443

COPY etc/ytdl-server.ini /etc/ytdl-server.ini

ENV YTDL_CFG_FILE="/etc/ytdl-server.ini"
#This YTDL_LOG_FILE var works, but I'm going to move the logs into systemd daemon logs when I make the process into a service.  This line will only be used for testing:
#ENV YTDL_LOG_FILE="/var/log/ytdl_server.log"

ENTRYPOINT ["python3", "/usr/local/lib/python3.10/dist-packages/ytdl_server/main.py"]
