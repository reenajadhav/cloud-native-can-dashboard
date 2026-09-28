import redis
import time
import random
from pathlib import Path
import json

from prometheus_client import Counter
from prometheus_client import start_http_server


frames_generated = Counter(
    'can_frames_generated_total',
    'Total CAN Frames Generated'
)

start_http_server(8000)

# -----------------------------------------------------
# connect to redis
# -----------------------------------------------------
def connect_to_redis():
    redis_obj = redis.Redis(
        host="redis",
        port=6379,
        decode_responses=True
    )
    print(redis_obj.ping())
    return redis_obj

# -----------------------------------------------------
# Simulate Vehicle CAN Messages
# -----------------------------------------------------
def write_raw_canlog_to_table():
    redis_set = connect_to_redis()
    last_timestamp = redis_set.get("last_timestamp")

    if last_timestamp is None:
        timestamp = time.time()
    else:
        timestamp = float(last_timestamp)

    # Initial simulated vehicle values
    speed = 25
    voltage = 24
    soc = 80

    while True:

        speed += random.randint(-2, 2)
        speed = max(0, min(speed, 120))

        voltage += random.randint(-1, 1)
        voltage = max(20, min(voltage, 30))

        soc -= random.choice([0, 0.5, 1])
        if soc < 15:
            soc = 80
        soc = round(soc, 1)

        payload_1f0 = f"{speed:02X} 03 FF 00 55 AA 00 11"
        payload_120 = f"{voltage:02X} 00 00 00 00 00 00 00"
        payload_321 = f"{int(soc):02X} 00 00 00 00 00 00 00"

        frames = [
            ("1F0", payload_1f0),
            ("120", payload_120),
            ("321", payload_321)
        ]

        for can_id, payload in frames:
            data = {
                "timestamp": round(timestamp, 6),
                "channel": 1,
                "can_id": can_id,
                "direction": "Rx",
                "frame_type": "d",
                "dlc": 8,
                "payload": payload
            }
            redis_set.rpush(
                "vehicle_can",
                json.dumps(data)
            )
            frames_generated.inc()
            print("set:", data)
            timestamp = time.time()+ 0.01

        time.sleep(60)
        redis_set.set("last_timestamp", time.time())
