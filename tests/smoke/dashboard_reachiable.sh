docker run -d \
  --name dashboard-smoke \
  -p 8501:8501 \
  can-dashboard:${BUILD_NUMBER}

sleep 20

curl http://localhost:8501

docker rm -f dashboard-smoke
