# Build rewardcalculator
FROM golang:1.12-alpine as builder

RUN apk add --no-cache git make
ADD https://api.github.com/repos/icon-project/rewardcalculator/git/refs/heads/master version.json
RUN git clone https://github.com/icon-project/rewardcalculator.git /rewardcalculator

RUN cd /rewardcalculator && make linux

# Build T-Bears
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
COPY --from=builder /rewardcalculator/linux/icon_rc /usr/local/bin/
COPY --from=builder /rewardcalculator/linux/rctool /usr/local/bin/
COPY entry.sh /usr/local/bin
COPY tbears_server_config.json .
ADD genesis genesis

RUN ./genesis/install.sh \
    && rm -rf /root/.cache/pip
RUN ./genesis/sendtx.sh \
    && rm -rf genesis

EXPOSE 9000
ENTRYPOINT ["entry.sh"]
