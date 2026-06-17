def rssi_to_int(rssi):
    if rssi < -90:
        return 0
    elif -90 <= rssi < -80:
        return 1
    elif -80 <= rssi < -70:
        return 2
    else:
        return 3