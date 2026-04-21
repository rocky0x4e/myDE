import subprocess as sp
import json


class AudioDevice:
    def __init__(self, data={}):
        self.data = data

    @property
    def _properties(self):
        return self.data.get("properties")

    @property
    def state(self):
        return self.data.get("state")

    @property
    def desc(self):
        return self.data.get("description")

    @property
    def sinkName(self):
        return self.data.get("name")


class PACTL:
    @staticmethod
    def getDefaultSink():
        return sp.check_output(["pactl", "get-default-sink"]).decode("utf-8").strip()

    @staticmethod
    def listSinksJson():
        return json.loads(sp.check_output(["pactl", "-f", "json", "list", "sinks"]).decode("utf-8").strip())

    @staticmethod
    def openPulseVolumeControl():
        sp.Popen(["pavucontrol"])

    @staticmethod
    def setDefaultSink(sinkName):
        sp.Popen(["pactl", "set-default-sink", sinkName])

    @staticmethod
    def get_devices():
        return [AudioDevice(data) for data in PACTL.listSinksJson()]
