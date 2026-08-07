from lib.pactl import AudioDevice, PACTL as pactl
from lib.fuzzel import fuzzel
from time import sleep
PAVUCTL = 'Open Pavu Control'
REFRESH = "Reload"
SEP = " | "


class AudioDevMan:
    def __init__(self):
        self.devcies = []
        self.defaultSink = pactl.getDefaultSink()
        self.fz = fuzzel().makeTable().setMesg(f"Audio devices: Name{SEP}Dev index").hidePrompt()\
            .setOutputLines(10).setWindowWidth(50)

    def get_devices(self):
        self.devcies = pactl.get_devices()
        return self

    def dmenuSelectDev(self):
        for dev in self.devcies:
            icon = "sink-enabled" if dev.sinkName in self.defaultSink else "sink-disabled"
            self.fz.addTableRow(row=[dev.getScreenName(), dev.index], icon=icon)

        self.fz.fmtTable(SEP)
        self.fz.addItem(PAVUCTL, "audio-control")
        self.fz.addItem(REFRESH, "refresh")
        return self.fz.run()


def main():
    while True:
        man = AudioDevMan()
        man.get_devices()
        select = man.dmenuSelectDev().split(SEP)[-1]
        if select == REFRESH:
            sleep(0.3)
            continue
        if select == PAVUCTL:
            pactl.openPulseVolumeControl()
        else:
            pactl.setDefaultSink(select)
        break
