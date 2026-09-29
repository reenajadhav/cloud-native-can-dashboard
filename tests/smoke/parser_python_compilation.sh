docker run --rm \
  can-parser:${ env.BUILD_NUMBER } \
  python -m compileall /app
