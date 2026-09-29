docker run --rm \
  can-parser:${TAG} \
  timeout 20 python main.py

docker logs parser-smoke | grep "Starting CAN Parser"
