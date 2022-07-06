# Makefile for testing, artifact creation, and dockerization
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

devinstall:
	pip install -r requirements-dev.txt
	pip install -e .

test: devinstall
	pytest

clean-dist:
	test -d "$(ROOT_DIR)/dist" && \rm -r "$(ROOT_DIR)/dist" || echo "DIR: $(ROOT_DIR)/dist does not exist.  Making a new dir there."
	mkdir "$(ROOT_DIR)/dist"

install-dist-reqs:
	pip install -r requirements-build.txt

sdist:
	python3 setup.py sdist

clean-build: clean-dist install-dist-reqs sdist

release: devinstall test clean-build

docker-build:
	docker build --build-arg 'VERSION=1.1.0' --tag 'ytdl_server' --label '1.1.0' --force-rm .

docker-run:
	docker run -p 192.168.0.200:5001:8443 -it --rm ytdl_server:latest

docker-vol-mount:
	docker run -p 192.168.0.200:5001:8443 -v "$(ROOT_DIR)/ytdl_server/media:/opt/ytdl_server/media" -it --rm ytdl_server:latest

build-all: release docker-build

docker-quicktest: build-all docker-run

docker-fullrun: build-all docker-vol-mount
