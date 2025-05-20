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
        self.rofi = rofi().makeDmenu().setPrompt('Bluetooth').setTheme('overlays/center-dialog')

    def isBtOn(self):
        pass

    def isConnected(self, dev):
        return self.devices[dev].get('isConnected', False)

    def prettyRofiList(self):
        for name in self.devices.keys():
            icon = 'bt-connected' if self.isConnected(name) else 'bt-disconnected'
            self.rofi.addItem(name, icon)

        self.rofi.addItem(blueMan, "bt-app")
        self.rofi.addItem(reload, "refresh")
        return self.rofi.run()

    def rofiActionOnDev(self, dev):
        try:
            if self.isConnected(dev):
                self.rofi.makeDmenu()
                self.rofi.addItem("disconnect", "bt-disconnected")
                self.rofi.addItem("reconnect", "bt-re-pair")
                return self.rofi.run()
            else:
                return "connect"
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

    def connect(self, name):
        btctl.actOnDev(self.devices[name]["addr"], "connect")
        return self

    def disconnect(self, name):
        btctl.actOnDev(self.devices[name]["addr"], "disconnect")
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
            self.disconnect(dev)
            self.waitStateChange(dev)
            self.connect(dev)
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
