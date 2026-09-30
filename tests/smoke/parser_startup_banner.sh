#!/bin/bash
set -e

docker run -d \
  --name parser-smoke \
  can-parser:${BUILD_NUMBER} \
  timeout 20 python main.py
docker logs parser-smoke | grep "Starting CAN Parser"
docker rm -f parser-smoke
