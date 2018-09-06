TAG=latest
IMAGE=tbears
LISTEN_PORT=9000

build:
	docker build -t $(IMAGE) .
run:
	docker run -it --name tbears-container -p $(LISTEN_PORT):9000 $(IMAGE)
shell:
	docker run -it -p $(LISTEN_PORT):9000 --rm --entrypoint /bin/bash $(IMAGE)
