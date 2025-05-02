import subprocess as sp
import json
from rockytools import rofi

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

    def nameAndIcon(self, defaultSink):
        icon = "sink-enabled" if self.sinkName in defaultSink else "sink-disabled"
        return self.desc, icon


class AudioDevMan:
    def __init__(self):
        self.devcies = []
        self.defaultSink = sp.check_output(["pactl", "get-default-sink"]).decode("utf-8")
        self.rofi = rofi('-dmenu', '-theme', 'overlays/center-dialog', '-icon-theme', 'rofi',
                         '-p', 'Audio Control', '-theme+inputbar+children', '[ prompt ]')

    def get_devices(self):
        data = json.loads(sp.check_output(["pactl", "-f", "json", "list", "sinks"]).decode("utf-8"))
        self.devcies = [AudioDevice(data) for data in data]
        return self

    def findDev(self, desc):
        for dev in self.devcies:
            if dev.desc == desc:
                return dev

    def rofiListDev(self):
        self.rofi.newMenu()
        for dev in self.devcies:
            self.rofi.addItem(*dev.nameAndIcon(self.defaultSink))

        self.rofi.addItem(PAVUCTL, "audio-control")
        self.rofi.addItem(REFRESH, "refresh")
        return self.rofi.run()

    def setDefaultSink(self, sinkDesc):
        sink = self.findDev(sinkDesc)
        print(sink)
        r = sp.check_output(["pactl", "set-default-sink", sink.sinkName]).decode("utf-8").strip()


def main():
    while True:
        man = AudioDevMan()
        man.get_devices()
        select = man.rofiListDev()
        if select == REFRESH:
            continue
        if select == PAVUCTL:
            sp.Popen(["pavucontrol"])
        else:
            man.setDefaultSink(select)
        break
