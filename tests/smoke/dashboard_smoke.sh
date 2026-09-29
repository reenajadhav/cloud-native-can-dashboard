#!/bin/bash
set -e

docker run -d \
  --name dashboard-smoke \
  can-dashboard:${ env.BUILD_NUMBER }

sleep 15

docker ps | grep dashboard-smoke

docker rm -f dashboard-smoke
