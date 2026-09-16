def decode(data):
    """
    CAN ID 120
    Vehicle Speed
    """

    if isinstance(data, str):
        data_bytes = [int(x, 16) for x in data.split()]
    else:
        data_bytes = data

    speed = data_bytes[0]

    return {
        "signal": "VehicleSpeed",
        "value": speed,
        "unit": "km/h"
    }