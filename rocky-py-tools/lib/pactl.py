import subprocess as sp
import json


def getDefaultSink():
    return sp.check_output(["pactl", "get-default-sink"]).decode("utf-8").strip()


def listSinksJson():
    return json.loads(sp.check_output(["pactl", "-f", "json", "list", "sinks"]).decode("utf-8").strip())


def openPulseVolumeControl():
    sp.Popen(["pavucontrol"])


def setDefaultSink(sinkName):
    sp.Popen(["pactl", "set-default-sink", sinkName])
