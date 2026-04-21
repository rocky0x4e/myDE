from lib.pactl import AudioDevice, PACTL as pactl
from lib.rofi import rofi
from time import sleep
PAVUCTL = 'Open Pavu Control'
REFRESH = "Reload"


class AudioDevMan:
    def __init__(self):
        self.devcies = []
        self.defaultSink = pactl.getDefaultSink()
        self.rofi = rofi().setInputBarChildren('[ prompt ]')\
            .makeDmenu().setPrompt('Audio Control').setTheme("overlays/center-dialog")

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
            self.rofi.addItem(*self.makeRofiItem(dev, self.defaultSink))

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
            sleep(0.3)
            continue
        if select == PAVUCTL:
            pactl.openPulseVolumeControl()
        else:
            man.setDefaultSink(select)
        break
