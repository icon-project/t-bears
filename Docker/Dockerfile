FROM python:3.7.3-slim-stretch

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libc-dev \
    pkg-config \
    libsecp256k1-dev \
    rabbitmq-server \
    vim-tiny \
    lsof \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY entry.sh /usr/local/bin
COPY tbears_server_config.json .
ADD genesis genesis

RUN ./genesis/install.sh \
    && rm -rf /root/.cache/pip
RUN ./genesis/sendtx.sh \
    && rm -rf genesis

EXPOSE 9000
ENTRYPOINT ["entry.sh"]
