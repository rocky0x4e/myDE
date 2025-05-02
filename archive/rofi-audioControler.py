#!/usr/bin/env python3

import subprocess as sp
import json

I = "\\x00icon\\x1f"
PAVUCTL='Open Pavu Control'
REFRESH = "Reload"
class AudioDevice:
    def __init__(self,data):
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

    def pretty(self,defaultSink):
        icon="sink-enabled" if self.sinkName in defaultSink else "sink-disabled"
        return f"{self.desc}{I}{icon}"

class AudioDevMan:
    def __init__(self):
        self.devcies =  []
        self.defaultSink = sp.check_output(["pactl", "get-default-sink"]).decode("utf-8")


    def get_devices(self):
        data = json.loads(sp.check_output(["pactl", "-f", "json", "list", "sinks"]).decode("utf-8"))
        self.devcies= [AudioDevice(data) for data in data]
        return self

    def findDev(self, desc):
        for dev in self.devcies:
            if dev.desc == desc:
                return dev

    def rofiListDev(self):
        options = ""
        for dev in self.devcies:
            options+= f"{dev.pretty(self.defaultSink)}\n"

        options+= f"{PAVUCTL}{I}audio-control\n{REFRESH}{I}refresh"

        pecho=sp.Popen(["echo", "-en", options],stdout=sp.PIPE,stderr=sp.PIPE)
        return sp.check_output(["rofi",'-dmenu', '-theme', 'overlays/center-dialog','-icon-theme','rofi',
                                '-p', 'Audio Control',
                                '-theme+inputbar+children', '[ prompt ]'],
                                stdin=pecho.stdout).decode("utf-8").strip()


    def setDefaultSink(self, sinkDesc):
        sink = self.findDev(sinkDesc)
        print(sink)
        r=sp.check_output(["pactl", "set-default-sink", sink.sinkName]).decode("utf-8").strip()

while True:
    man = AudioDevMan()
    man.get_devices()
    select = man.rofiListDev()
    if select == REFRESH: continue
    if select == PAVUCTL:
        sp.Popen(["pavucontrol"])
    else:
        man.setDefaultSink(select)
    break
