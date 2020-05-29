VERSION=1.6.2
IMAGE_TAG=iconloop/tbears:$(VERSION)
LISTEN_PORT=9000

build:
	docker build -t $(IMAGE_TAG) .

run:
	docker run -it -p $(LISTEN_PORT):9000 --rm $(IMAGE_TAG)

shell:
	docker run -it -p $(LISTEN_PORT):9000 --rm --entrypoint /bin/bash $(IMAGE_TAG)
