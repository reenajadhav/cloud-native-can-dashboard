#!/bin/bash

set -e

echo "Dashboard reachability check..."

docker rm -f dashboard-smoke >/dev/null 2>&1 || true

docker run -d \
  --name dashboard-smoke \
  -p 8501:8501 \
  can-dashboard:${BUILD_NUMBER}

sleep 20

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)

if [ "$STATUS" != "200" ]; then
    echo "FAIL - Dashboard returned HTTP ${STATUS}"
    docker logs dashboard-smoke
    docker rm -f dashboard-smoke
    exit 1
fi

docker rm -f dashboard-smoke

echo "PASS - Dashboard reachable"
