docker run -d \
  --name simulator-smoke \
  vehicle-simulator:${TAG}

sleep 10

docker ps | grep simulator-smoke

docker rm -f simulator-smoke
