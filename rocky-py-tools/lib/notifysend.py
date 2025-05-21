import subprocess as sp
from pathlib import Path

ROFI_ICO_PATH = Path.home() / ".local/share/icons/rofi/512x512/apps"


def _getRofiImage(name):
    for item in ROFI_ICO_PATH.iterdir():
        if name in item.name:
            return str(item.absolute())


class NotifySend:
    def __init__(self):
        self.args = ['-p']
        self.kwargs = {
            "-t": "5000",
            "-u": "normal",
            "-a": "",
            "-c": "",
            "-i": ""
        }
        self.title = ""
        self.message = ""
        self.prevId = ""

    def setTitle(self, title):
        self.title = title
        return self

    def setMessage(self, message):
        self.message = message
        return self

    def setTimeout(self, ms):
        self.kwargs['-t'] = str(ms)
        return self

    def setTransient(self):
        self.args.append("-e")
        return self

    def printId(self):
        self.args.append("-p")
        return self

    def setUrgencyLow(self):
        self.kwargs['-u'] = "low"
        return self

    def setUrgencyNormal(self):
        self.kwargs['-u'] = "normal"
        return self

    def setUrgencyCrit(self):
        self.kwargs['-u'] = "critical"
        return self

    def setIcon(self, icon):
        self.kwargs["-i"] = icon
        return self

    def addHint(self, hint):
        self.args.extend(["--hint", hint])
        return self

    def setRofiImage(self, image):
        self.addHint(f"string:image-path:file://{_getRofiImage(image)}")
        return self

    def setGtkImage(self, image):
        self.addHint(f"string:image-path:{image}")
        return self

    def setAppName(self, appName):
        self.kwargs["-a"] = appName
        return self

    def flash(self, replace=False):
        args = self.args
        if replace:
            args.extend(["-r", self.prevId])
        for k, v in self.kwargs.items():
            args.extend([k, v]) if v else None
        self.prevId = sp.check_output(["notify-send", *args,
                                       self.title, self.message]).decode().strip()
