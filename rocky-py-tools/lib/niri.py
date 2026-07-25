import subprocess as sp
import json


class niriwm:
    @staticmethod
    def listWindows():
        return niriWindowList(sp.run(["niri", "msg", "--json", "windows"]).stdout.decode())


class niriWindowList:
    def __init__(self, data) -> None:
        self.windowList = json.loads(data)

    def findWindowAppId(self, **kwargs):
        name = kwargs.get("name")
        for window in self.windowList:
            if window.get("app-id") == name:
                return window.get('id')
