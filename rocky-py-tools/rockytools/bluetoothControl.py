from time import sleep
from lib.rofi import rofi
from lib import bluetoothctl as btctl

blueMan = 'Open Blueman'
reload = 'Reload'
btOff = 'Turn off Bluetooth'
bt_On = 'Turn on Bluetooth'


class BtControl:
    def __init__(self):
        self.devices = btctl.listDevices()
        self.rofi = rofi('-dmenu', '-p', 'Bluetooth', '-icon-theme', 'rofi', '-theme', 'overlays/center-dialog')

    def isBtOn(self):
        pass

    def isConnected(self, dev):
        return self.devices[dev].get('isConnected', False)

    def prettyRofiList(self):
        self.rofi.makeDmenu()
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
                self.rofi.makeDmenu()
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
            self.devices = btctl.listDevices()
            timeout -= 1
        return self

    def toggle(self, name):
        action = "disconnect" if self.isConnected(name) else "connect"
        btctl.actOnDev(self.devices[name]["addr"], action)
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
            btctl.openBlueMan()
            return self

        print(action, "is not yet support")


def main():
    while True:
        bman = BtControl()
        selected = bman.prettyRofiList()
        if selected == reload:
            continue
        action = bman.rofiActionOnDev(selected)
        bman.handleActionOnDev(action, selected)
        break
