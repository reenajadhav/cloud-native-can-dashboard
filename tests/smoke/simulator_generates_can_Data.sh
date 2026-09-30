docker run -d \
  --name simulator-smoke \
  vehicle-simulator:${BUILD_NUMBER}

sleep 20

docker logs simulator-smoke

docker logs simulator-smoke | grep -q "Publishing CAN frames"

docker rm -f simulator-smoke
