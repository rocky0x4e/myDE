from lib import pactl
from lib.rofi import rofi

PAVUCTL = 'Open Pavu Control'
REFRESH = "Reload"


class AudioDevice:
    def __init__(self, data):
        self.data = data

    @property
    def _properties(self):
        return self.data["properties"]

    @property
    def state(self):
        return self.data["state"]

    @property
    def desc(self):
        return self.data["description"]
        # return self._properties["device.description"]

    @property
    def sinkName(self):
        return self.data["name"]

    def rofiItem(self, defaultSink):
        icon = "sink-enabled" if self.sinkName in defaultSink else "sink-disabled"
        return self.desc, icon


class AudioDevMan:
    def __init__(self):
        self.devcies = []
        self.defaultSink = pactl.getDefaultSink()
        self.rofi = rofi('-dmenu', '-theme', 'overlays/center-dialog', '-icon-theme', 'rofi',
                         '-p', 'Audio Control', '-theme+inputbar+children', '[ prompt ]')

    def get_devices(self):
        data = pactl.listSinksJson()
        self.devcies = [AudioDevice(data) for data in data]
        return self

    def findDev(self, desc):
        for dev in self.devcies:
            if dev.desc == desc:
                return dev

    def rofiListDev(self):
        self.rofi.makeDmenu()
        for dev in self.devcies:
            self.rofi.addItem(*dev.rofiItem(self.defaultSink))

        self.rofi.addItem(PAVUCTL, "audio-control")
        self.rofi.addItem(REFRESH, "refresh")
        return self.rofi.run()

    def setDefaultSink(self, sinkDesc):
        sink = self.findDev(sinkDesc)
        pactl.setDefaultSink(sink.sinkName)


def main():
    while True:
        man = AudioDevMan()
        man.get_devices()
        select = man.rofiListDev()
        if select == REFRESH:
            continue
        if select == PAVUCTL:
            pactl.openPulseVolumeControl()
        else:
            man.setDefaultSink(select)
        break
