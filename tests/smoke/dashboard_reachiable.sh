docker run -d \
  --name dashboard-smoke \
  -p 8501:8501 \
  can-dashboard:${TAG}

sleep 20

curl http://localhost:8501

docker rm -f dashboard-smoke
