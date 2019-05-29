# Dockerfile for T-Bears Container

This document describes how to build a T-Bears Docker image and run the image as a Docker container.

## Requirements
* [Docker](https://docs.docker.com/)

## Base Docker Image

* python:3.7.3-slim-stretch

## Build T-Bears Docker Image
```
$ make build
```

Note that you don't need to build the Docker image by yourself.
The official Docker images for T-Bears are available from the Docker Hub: [https://hub.docker.com/r/iconloop/tbears](https://hub.docker.com/r/iconloop/tbears).
You can download the T-Bears Docker image by using the `docker pull` command.

```
$ docker pull iconloop/tbears:mainnet
```

The `mainnet` tag has been attached to the Docker image that is same with the ICON Mainnet environment.

## Usage

### Running T-Bears Docker Container

```
$ make run
```

or

```
$ docker run -it -p 9000:9000 iconloop/tbears:mainnet
```

This will start the T-Bears container that is listening on port 9000 for incoming requests.
If you want the T-Bears container to listen on a different port, replace `${LISTEN_PORT}` with your desired port number.

```
$ docker run -it -p ${LISTEN_PORT}:9000 iconloop/tbears:mainnet
```

### Test with T-Bears Docker Container

#### From the Container
In the same terminal, run the following T-Bears CLI command to see if the T-Bears service is working correctly.
```bash
root@27cadb5e0047:/work# tbears totalsupply
Total supply of ICX in hex: 0x52c3fff19494c464f000000
Total supply of ICX in decimal: 1600920000000000000000000000
```

#### From the Host System
From another terminal, run the following T-Bears CLI command to see if it could be correctly connected to the T-Bears service.

If you modified the listening port of T-Bears container, run the T-Bears CLI command with `-u` option.

```bash
(.venv) /work $ tbears totalsupply -u http://127.0.0.1:9000/api/v3
Total supply of ICX in hex: 0x52c3fff19494c464f000000
Total supply of ICX in decimal: 1600920000000000000000000000
```
Note that you don't need to install RabbitMQ package on the host system in this configuration. Just need to install T-Bears package for issuing some CLI commands.


## License

This project follows the Apache 2.0 License. Please refer to [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.
