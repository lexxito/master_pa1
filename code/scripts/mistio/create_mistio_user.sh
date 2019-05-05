#!/usr/bin/env bash
docker-compose exec api sh -c "./bin/adduser --admin $1 --password $2"
