import subprocess as sp
from pathlib import Path

ROFI_ICO_PATH = Path.home() / ".local/share/icons/rofi/512x512/apps"


def _getRofiImage(name):
    for item in ROFI_ICO_PATH.iterdir():
        if name in item.name:
            return str(item.absolute())


class NotifySend:
    def __init__(self):
        self.args = []
        self.kwargs = {
            "-t": "5000",
            "-u": "normal",
            "-a": "",
            "-c": "",
            "-i": ""
        }
        self.title = ""
        self.message = ""

    def setTitle(self, title):
        self.title = title
        return self

    def setMessage(self, message):
        self.message = message
        return self

    def setTimeout(self, timeout):
        self.kwargs['-t'] = str(timeout)
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

    def flash(self):
        args = self.args
        for k, v in self.kwargs.items():
            args.extend([k, v]) if v else None
        sp.check_output(["notify-send", *args,
                         self.title, self.message]).decode().strip()
