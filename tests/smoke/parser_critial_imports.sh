docker run --rm \
  can-parser:${TAG} \
  python -c "
from decoders.decoder_1F0 import decode
from decoders.decoder_120 import decode
from decoders.decoder_321 import decode
print('PASS')
