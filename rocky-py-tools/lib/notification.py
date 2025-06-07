import subprocess as sp
from pathlib import Path

ROFI_ICO_PATH = Path.home() / ".local/share/icons/rofi/512x512/apps"


def _getRofiImage(name):
    for item in ROFI_ICO_PATH.iterdir():
        if name in item.name:
            return str(item.absolute())


class Notifier:
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
        self.notifier = ''

    def setTitle(self, title):
        self.title = title
        return self

    def setMessage(self, message):
        self.message = str(message)
        return self

    def setTimeout(self, ms):
        self.kwargs['-t'] = str(ms)
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
        self.args.extend(["-h", hint])
        return self

    def clearHint(self):
        skipIndex = []
        i = 0
        while i < len(self.args):
            if self.args[i] == "-h":
                skipIndex.extend([i, i+1])
                i += 1
            i += 1
        newArg = []
        for i in range(len(self.args)):
            if i in skipIndex:
                continue
            newArg.append(self.args[i])
        self.args = newArg

    def setAppName(self, appName):
        self.kwargs["-a"] = appName
        return self

    def printId(self):
        self.args.append("-p")
        return self

    def flash(self, **kwargs):
        args = [*self.args]
        for k, v in self.kwargs.items():
            args.extend([k, v]) if v else None

        replace = kwargs.get("replace", False)
        wait = kwargs.get("wait", False)
        timeout = kwargs.get("timeout", None)
        if replace:
            args.extend(["-r", self.prevId]) if self.prevId else None
        if wait:
            args.extend(["-w"])
        if timeout:
            timeout = str(int(timeout * 1000))
            try:
                tIndex = args.index("-t")
                args[tIndex+1] = timeout
            except ValueError:
                args.extend(["-t", timeout])
        result = sp.check_output([self.notifier, *args,
                                  self.title, self.message]).decode().strip()
        self.prevId = result.splitlines()[0]
        return result


class NotifySend(Notifier):
    def __init__(self):
        super().__init__()
        self.notifier = 'notify-send'

    def setTransient(self, state=True):
        self.args.append("-e") if state else self.args.remove("-e")
        return self

    def setWait(self, state=True):
        self.args.append("-w") if state else self.args.remove("-w")
        return self

    def setRofiImage(self, image):
        self.addHint(f"string:image-path:file://{_getRofiImage(image)}")
        return self

    def setGtkImage(self, image):
        self.addHint(f"string:image-path:{image}")
        return self

    def setAction(self, *args):
        return self


class DunstCtl(Notifier):
    def __init__(self):
        super().__init__()
        self.notifier = "dunstify"
        self.actionCallback = {}

    def setRofiImage(self, image):
        self.kwargs["-I"] = _getRofiImage(image)
        return self

    def setWait(self, state=True):
        return self

    def setTransient(self, state=True):
        self.addHint('int:transient:1' if state else 'int:transient:0')
        return self

    def addAction(self, action, label, callback=None):
        self.args.extend(['-A', f"{action},{label}"])
        self.actionCallback[action] = callback
        return self

    def flash(self, **kwargs):
        r = super().flash(**kwargs).splitlines()
        try:
            action = r[1]
            self.actionCallback[action]()
        except (IndexError, KeyError):
            pass


DefautNotifier = DunstCtl
