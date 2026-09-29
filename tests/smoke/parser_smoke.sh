#!/bin/bash
set -e

echo "Parser import check..."

docker run --rm \
  can-parser:${ env.BUILD_NUMBER } \
  python -c "
from decoders.decoder_1F0 import decode
from decoders.decoder_120 import decode
from decoders.decoder_321 import decode
print('PASS')
