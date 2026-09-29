def decode(data):

    if isinstance(data, str):
        data = [int(x, 16) for x in data.split()]

    rpm = (data[1] << 8) | data[0]

    return {
        "signal": "EngineRPM",
        "value": rpm,
        "unit": "rpm"
    }