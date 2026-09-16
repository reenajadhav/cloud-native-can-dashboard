from pathlib import Path
import sqlite3
import redis
import json
from decoders.decoder_1F0 import decode as decoder_1F0
from decoders.decoder_120 import decode as decoder_120
from decoders.decoder_321 import decode as decoder_321

from prometheus_client import Counter, Gauge, start_http_server, Gauge

# -----------------------------------------------------
# Database Paths
# -----------------------------------------------------
DECODED_DB = Path("/shared/decoded.db")

# -----------------------------------------------------
# Decoder Map
# -----------------------------------------------------

DECODER_MAP = {
    "1F0": decoder_1F0,
    "120": decoder_120,
    "321": decoder_321,
}

# -----------------------------------------------------
# promethesus counter
# -----------------------------------------------------
decoded_messages_total = Counter(
    "decoded_messages_total",
    "Total CAN messages successfully decoded"
)

sqlite_writes_total = Counter(
    "sqlite_writes_total",
    "Total rows written to SQLite"
)

redis_queue_depth = Gauge(
    "redis_queue_depth",
    "Current number of messages waiting in Redis queue"
)
start_http_server(8001)
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
# Create decoded database table
# -----------------------------------------------------

def create_decoded_table():

    conn = sqlite3.connect(DECODED_DB)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS decoded_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        can_id TEXT,
        signal_name TEXT,
        signal_value REAL,
        unit TEXT
    )
    """)

    conn.commit()
    conn.close()

# -----------------------------------------------------
# Store decoded signal
# -----------------------------------------------------

def store_decoded_signal(
        timestamp,
        can_id,
        signal_name,
        signal_value,
        unit
):

    conn = sqlite3.connect(DECODED_DB)

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO decoded_signals (
        timestamp,
        can_id,
        signal_name,
        signal_value,
        unit
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        timestamp,
        can_id,
        signal_name,
        signal_value,
        unit
    ))

    conn.commit()
    sqlite_writes_total.inc()
    conn.close()

# -----------------------------------------------------
# Read CAN database
# -----------------------------------------------------

def read_can_database():
    redis_obj = connect_to_redis()

    # redis queue size
    queue_size = redis_obj.llen("vehicle_can")
    redis_queue_depth.set(queue_size)

    msg = redis_obj.blpop("vehicle_can")
    if msg is None:
        return None
    data = json.loads(msg[1])
    return data

# -----------------------------------------------------
# Decode CAN frames
# -----------------------------------------------------

def decode_can_frames():

    row = read_can_database()

    print(f"Raw CAN Frames Found : {row}")
    if row is None:
        return
    timestamp = row["timestamp"]
    can_id = row["can_id"].strip().upper()      
    payload = row["payload"]

    decoder = DECODER_MAP.get(can_id)
    decoded_messages_total.inc()

    try:

        decoded = decoder(payload)

        # Expected decoder output:
        #
        # {
        #     "signal": "EngineRPM",
        #     "value": 792.0,
        #     "unit": "rpm"
        # }

        signal_name = decoded["signal"]
        signal_value = decoded["value"]
        unit = decoded["unit"]

        store_decoded_signal(
            timestamp,
            can_id,
            signal_name,
            signal_value,
            unit
        )

        print(
            f"{timestamp:.3f} | "
            f"{can_id} | "
            f"{signal_name} = "
            f"{signal_value} {unit}"
        )

    except Exception as e:

        print(
            f"Decode Error | "
            f"CAN_ID={can_id} | "
            f"Payload={payload} | "
            f"Error={e}"
        )

