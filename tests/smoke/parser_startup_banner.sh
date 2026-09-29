docker run --rm \
  can-parser:${BUILD_NUMBER} \
  timeout 20 python main.py

docker logs parser-smoke | grep "Starting CAN Parser"
