import subprocess as sp
import json
from typing import Dict, List, Union


class niriWindow:
    def __init__(self, data) -> None:
        self.data = data

    @property
    def id(self):
        return self.data['id']

    @property
    def appId(self):
        return self.data['app_id']

    @property
    def appIdSort(self):
        return self.data['app_id'][:15]

    @property
    def pid(self):
        return self.data['pid']

    @property
    def isFocused(self):
        return self.data['is_focused']

    @property
    def workspaceId(self):
        return self.data['workspace_id']

    @property
    def title(self):
        return self.data['title']


class niriWindowList:
    def __init__(self, listData) -> None:
        self.windowList: List[niriWindow] = []
        for item in listData:
            if type(item) is dict:
                self.windowList.append(niriWindow(item))
            elif type(item) is niriWindow:
                self.windowList.append(item)
            else:
                raise TypeError(f"Unsupported type: {item}")

    def findWindow(self, **kwargs):
        appid = kwargs.get("appid")
        for window in self.windowList:
            if window.appId == appid:
                return window

    def findWindows(self, **kwargs):
        res = []
        appid = kwargs.get("appid")
        for window in self.windowList:
            if window.appId == appid:
                res.append(window)
        return res

    def groupByWorkspaceId(self) -> Dict[str, List[niriWindow]]:
        groups = {}
        for w in self.windowList:
            try:
                groups[w.workspaceId].append(w)
            except KeyError:
                groups[w.workspaceId] = [w]
        return groups


class niriWorkspace:
    def __init__(self, data) -> None:
        self.data: Dict = data

    @property
    def id(self):
        return self.data['id']

    @property
    def idx(self):
        return self.data['idx']

    @property
    def name(self):
        return self.data.get('name', '-')

    @property
    def activeWindowId(self):
        return self.data.get('active_window_id')


class niriWorkspaceList:
    def __init__(self, listData) -> None:
        self.workspaces: Dict[str, niriWorkspace] = {ws['id']: niriWorkspace(ws) for ws in listData}

    def getWsById(self, id):
        return self.workspaces[id]


class niriwm:
    @staticmethod
    def getWindows():
        return niriWindowList(json.loads(sp.check_output(["niri", "msg", "--json", "windows"]).decode()))

    @staticmethod
    def focusWindow(window: Union[niriWindow, str, int]):
        if type(window) is niriWindow:
            id = window.id
        elif type(window) is int or type(window) is str:
            id = window
        else:
            raise TypeError()
        sp.call(["niri", "msg", "action", "focus-window", "--id", str(id)])

    @staticmethod
    def getFocusedWindow():
        data = sp.check_output(["niri", "msg", "--json", "focused-window"]).decode()
        return niriWindow(json.loads(data))

    @staticmethod
    def getWorkspaces():
        data = sp.check_output(["niri", "msg", "--json", "workspaces"]).decode()
        return niriWorkspaceList(json.loads(data))
