docker run -d \
  --name simulator-smoke \
  vehicle-simulator:${ env.BUILD_NUMBER }

sleep 20

docker logs simulator-smoke

docker rm -f simulator-smoke
