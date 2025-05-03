import subprocess as sp


class NotifySend:
    def __init__(self):
        self.args = []
        self.kwargs = {
            "-t": "5000",
            "-u": "normal",
            "-a": "",
            "-c": "",
            "-h": "",
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

    def setAppName(self, appName):
        self.kwargs["-a"] = appName
        return self

    def flash(self):
        args = self.args
        for k, v in self.kwargs.items():
            args.extend([k, v]) if v else None
        sp.check_output(["notify-send", *args,
                         * self.args, self.title, self.message]).decode().strip()
