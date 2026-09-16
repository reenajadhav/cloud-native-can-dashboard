import time
from parser import create_decoded_table, decode_can_frames

if __name__ == "__main__":

    print("Starting CAN Parser...")

    create_decoded_table()

    while True:
        decode_can_frames()
