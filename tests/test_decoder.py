def test_speed_decode():
    speed = decode_speed("10000000")
    assert speed == 16

