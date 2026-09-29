docker run -d \
  --name dashboard-smoke \
  can-dashboard:${BUILD_NUMBER}

sleep 15

docker exec dashboard-smoke \
  ss -lnt

docker rm -f dashboard-smoke
