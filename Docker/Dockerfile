FROM ubuntu:18.04

# Install required packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.6-dev \
    python3-pip \
    python3-setuptools \
    gcc \
    git \
    pkg-config \
    libsecp256k1-dev \
    rabbitmq-server \
    locales \
    vim-tiny \
    lsof \
    && locale-gen en_US.UTF-8 \
    && pip3 install wheel \
    && pip3 install tbears \
    && apt autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip

# Add default locale
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Set working directory
ENV WORKING_DIR "/tbears"
WORKDIR ${WORKING_DIR}
VOLUME tbears_volume
COPY entry.sh /usr/local/bin

EXPOSE 9000

ENTRYPOINT ["entry.sh"]
