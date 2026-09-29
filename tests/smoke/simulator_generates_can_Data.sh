docker run -d \
  --name simulator-smoke \
  vehicle-simulator:${TAG}

sleep 20

docker logs simulator-smoke

docker rm -f simulator-smoke
