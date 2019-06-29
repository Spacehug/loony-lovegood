#!/usr/bin/env bash
# Tab sign preceded and followed by spaces: 	 .

install:
	docker-compose -f dockerfiles/docker-compose.yml -p LOONY up -d --build
