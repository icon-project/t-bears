IMAGE=iconloop/tbears
LISTEN_PORT=9000

ifneq ($(branch),)
	BUILD_ARG:= $(BUILD_ARG) --build-arg branch=$(branch)
endif

ifneq ($(tag),)
	IMAGE_TAG=:$(tag)
	NAME_TAG=-$(tag)
endif

build:
	docker build -t $(IMAGE) .
build_dev:
	docker build -t $(IMAGE):dev --no-cache -f Dockerfile.dev . $(BUILD_ARG)
run:
	docker run -it --name tbears-container$(NAME_TAG) -p $(LISTEN_PORT):9000 $(IMAGE)$(IMAGE_TAG)
shell:
	docker run -it -p $(LISTEN_PORT):9000 --rm --entrypoint /bin/bash $(IMAGE)
