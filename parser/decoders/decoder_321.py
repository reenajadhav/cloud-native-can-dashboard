def decode(data):
    """
    CAN ID 321
    Fuel Level
    """

    if isinstance(data, str):
        data_bytes = [int(x, 16) for x in data.split()]
    else:
        data_bytes = data

    fuel = data_bytes[0]

    return {
        "signal": "FuelLevel",
        "value": fuel,
        "unit": "%"
    }