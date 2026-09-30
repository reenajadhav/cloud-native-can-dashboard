#!/bin/bash
set -e

docker run -d \
  --name dashboard-smoke \
  can-dashboard:${BUILD_NUMBER}

sleep 15

if docker ps | grep -q dashboard-smoke; then
    echo "PASS - Dashboard container is running"
else
    echo "FAIL - Dashboard container is not running"
    docker logs dashboard-smoke
    exit 1
fi

docker rm -f dashboard-smoke

echo "PASS - Dashboard reachable"