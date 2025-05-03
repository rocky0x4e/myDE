import subprocess as sp


def listDevices():
    """ List paired bluetooth device

    Returns:
        dict: {addr, name, isConnected}
    """
    data = sp.check_output(['bluetoothctl', "devices", "Paired"]).decode("utf-8").strip()
    devices = {}
    for line in data.splitlines():
        line = line.replace("Device ", "").strip()
        i = line.find(" ")
        addr = line[:i]
        name = line[i+1:]
        devices[name] = {"addr": addr, "name": name, "isConnected": False}

    data = sp.check_output(['bluetoothctl', "devices", "Connected"]).decode("utf-8").strip()
    for line in data.splitlines():
        line = line.replace("Device ", "").strip()
        i = line.find(" ")
        name = line[i+1:]
        devices[name]['isConnected'] = True

    return devices


def connectDev(addr):
    sp.Popen(["bluetoothctl", 'connect', addr])


def disconnectDev(addr):
    sp.Popen(["bluetoothctl", 'disconnect', addr])


def actOnDev(addr, action):
    sp.Popen(["bluetoothctl", action, addr])


def openBlueMan():
    sp.Popen(['blueman-manager'])
