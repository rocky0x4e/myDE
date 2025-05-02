import subprocess as sp
from time import sleep
from rockytools import rofi

isConnected = 'isConnected'
blueMan = 'Open Blueman'
reload = 'Reload'
btOff = 'Turn off Bluetooth'
bt_On = 'Turn on Bluetooth'


class BtControl:
    def __init__(self):
        self.devices = {}
        self.getPairedDevs()
        self.getConnectedDevs()
        self.rofi = rofi('-dmenu', '-p', 'Bluetooth', '-icon-theme', 'rofi', '-theme', 'overlays/center-dialog')

    def isBtOn(self):
        pass

    def getPairedDevs(self):
        self.devices = {}
        data = sp.check_output(['bluetoothctl', "devices", "Paired"]).decode("utf-8").strip()
        for line in data.splitlines():
            line = line.replace("Device ", "").strip()
            i = line.find(" ")
            addr = line[:i]
            name = line[i+1:]
            self.devices[name] = {"addr": addr, "name": name}

    def getConnectedDevs(self):
        data = sp.check_output(['bluetoothctl', "devices", "Connected"]).decode("utf-8").strip()
        for dev in self.devices.keys():
            self.devices[dev][isConnected] = False
        for line in data.splitlines():
            line = line.replace("Device ", "").strip()
            i = line.find(" ")
            name = line[i+1:]
            self.devices[name][isConnected] = True

    def isConnected(self, dev):
        return self.devices[dev].get(isConnected, False)

    def prettyRofiList(self):
        self.rofi.newMenu()
        for name in self.devices.keys():
            icon = 'bt-connected' if self.isConnected(name) else 'bt-disconnected'
            self.rofi.addItem(name, icon)

        self.rofi.addItem(blueMan, "bt-app")
        self.rofi.addItem(reload, "refresh")
        return self.rofi.run()

    def rofiActionOnDev(self, dev):
        try:
            if self.isConnected(dev):
                return "disconnect"
            else:
                self.rofi.newMenu()
                self.rofi.addItem("connect", "bt-connected")
                self.rofi.addItem("repair", "bt-re-pair")
            return self.rofi.run()
        except:
            return

    def waitStateChange(self, dev):
        timeout = 15
        state1 = self.isConnected(dev)
        while self.isConnected(dev) == state1 and timeout > 0:
            print(self.isConnected(dev))
            sleep(1)
            self.getConnectedDevs()
            timeout -= 1
        return self

    def toggle(self, name):
        action = "disconnect" if self.isConnected(name) else "connect"
        sp.Popen(["bluetoothctl", action, self.devices[name]["addr"]])
        return self

    def handleActionOnDev(self, action, dev):
        directActions = ['connect', 'disconnect']
        if action in directActions:
            return self.toggle(dev)

        if action == 'reconnect':
            self.toggle(dev)
            self.waitStateChange(dev)
            self.toggle(dev)
            return self
        if dev == blueMan:
            self.openBlueMan()
            return self

        print(action, "is not yet support")

    def openBlueMan(self):
        sp.Popen(['blueman-manager'])


def main():
    while True:
        bman = BtControl()
        selected = bman.prettyRofiList()
        if selected == reload:
            continue
        action = bman.rofiActionOnDev(selected)
        bman.handleActionOnDev(action, selected)
        break
