VERSION=$(shell cat ../VERSION)
IMAGE_TAG=iconloop/tbears:$(VERSION)
LISTEN_PORT=9000
RC_REPO=icon-project/rewardcalculator
RC_TAG=$(shell curl --silent "https://api.github.com/repos/$(RC_REPO)/releases/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

make_env:
	@echo "RC_REPO=$(RC_REPO)" > .env
	@echo "VERSION=$(VERSION)" >> .env
	@echo "IMAGE_TAG=iconloop/tbears:$(VERSION)" >> .env
	@echo "LISTEN_PORT=9000" >> .env
	@echo "RC_TAG=$(RC_TAG)" >> .env

build:
	@docker-compose build

shell:
	@docker run -it --rm --network=host --entrypoint /bin/bash $(IMAGE_TAG)

start_mq:
	@docker-compose up -d rabbitmq

start_tbears:
	@docker-compose up -d tbears

start:
	@docker-compose up -d

start_cli:
	@docker-compose exec tbears bash

destroy:
	@docker-compose down