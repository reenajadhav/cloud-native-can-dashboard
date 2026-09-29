#!/bin/bash
set -e

docker run -d \
  --name simulator-smoke \
  vehicle-simulator:${ env.BUILD_NUMBER }

sleep 15

docker logs simulator-smoke

docker rm -f simulator-smoke
