# Build rewardcalculator
FROM golang:1.12-alpine as builder

ARG RC_TAG

RUN apk add --no-cache git make
ADD https://api.github.com/repos/icon-project/rewardcalculator/git/refs/heads/master version.json
RUN git clone --branch $RC_TAG --single-branch https://github.com/icon-project/rewardcalculator.git /rewardcalculator

RUN cd /rewardcalculator && make

# Build T-Bears
FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    libc-dev \
    pkg-config \
    vim-tiny \
    lsof \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY --from=builder /rewardcalculator/bin/icon_rc /usr/local/bin/
COPY --from=builder /rewardcalculator/bin/rctool /usr/local/bin/

COPY tbears_server_config.json .
ADD genesis genesis
ADD wait-for-amq.py .

RUN ./genesis/install.sh \
    && rm -rf /root/.cache/pip
RUN ./genesis/init.sh \
    && rm -rf genesis

EXPOSE 9000

COPY entry.sh /usr/local/bin
RUN chmod +x /usr/local/bin/entry.sh

ENTRYPOINT ["entry.sh"]
