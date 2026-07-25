from lib.pactl import AudioDevice, PACTL as pactl
from lib.fuzzel import fuzzel
from time import sleep
PAVUCTL = 'Open Pavu Control'
REFRESH = "Reload"


class AudioDevMan:
    def __init__(self):
        self.devcies = []
        self.defaultSink = pactl.getDefaultSink()
        self.fz = fuzzel().makeDmenu().setPrompt('Audio Control ').setOutputLines(10).setWindowWidth(50)

    def get_devices(self):
        self.devcies = pactl.get_devices()
        return self

    def findDev(self, desc) -> AudioDevice:
        for dev in self.devcies:
            if dev.desc == desc:
                return dev
        return AudioDevice()

    def makeRofiItem(self, dev, defaultSink):
        icon = "sink-enabled" if dev.sinkName in defaultSink else "sink-disabled"
        return dev.desc, icon

    def rofiListDev(self):
        for dev in self.devcies:
            self.fz.addItem(*self.makeRofiItem(dev, self.defaultSink))

        self.fz.addItem(PAVUCTL, "audio-control")
        self.fz.addItem(REFRESH, "refresh")
        return self.fz.run()

    def setDefaultSink(self, sinkDesc):
        sink = self.findDev(sinkDesc)
        pactl.setDefaultSink(sink.sinkName)


def main():
    while True:
        man = AudioDevMan()
        man.get_devices()
        select = man.rofiListDev()
        if select == REFRESH:
            sleep(0.3)
            continue
        if select == PAVUCTL:
            pactl.openPulseVolumeControl()
        else:
            man.setDefaultSink(select)
        break
