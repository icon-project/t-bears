VERSION=$(shell cat ../VERSION)
IMAGE_TAG=iconloop/tbears:$(VERSION)
LISTEN_PORT=9000
RC_REPO=icon-project/rewardcalculator
RC_TAG=$(shell curl --silent "https://api.github.com/repos/$(RC_REPO)/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

build:
	docker build -t $(IMAGE_TAG) --build-arg RC_TAG=$(RC_TAG) .

run:
	docker run -it -p $(LISTEN_PORT):9000 --rm $(IMAGE_TAG)

shell:
	docker run -it -p $(LISTEN_PORT):9000 --rm --entrypoint /bin/bash $(IMAGE_TAG)
