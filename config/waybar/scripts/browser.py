#!/usr/bin/env python3

import subprocess as sp
import json
from datetime import datetime
browsers = [
    {
        "xdgName": "brave-browser.desktop",
        "name": "Brave",
        "processName": "brave-browser",
        "wmclass": "Brave-browser",
        "icon": "brave",
    },
    {
        "xdgName": "google-chrome.desktop",
        "name": "Chrome",
        "processName": "^chrome$",
        "wmclass": "Google-chrome",
        "icon": "google-chrome",
    },
    {
        "xdgName": "opera.desktop",
        "name": "Opera",
        "processName": "^opera$",
        "wmclass": "Opera",
        "icon": "opera",
    },
    {
        "xdgName": "firefox.desktop",
        "name": "Firefox",
        "processName": "^firefox-bin$",
        "wmclass": "firefox",
        "icon": "firefox",
    }
]


def getCurrentBrowser():
    return sp.run(["xdg-settings", "get", "default-web-browser"], capture_output=True, text=True).stdout.strip()


def showCurrentBrowserOnWayBar():
    return json.dumps({"icon": "brave-browser", "text": datetime.now().second})


print(showCurrentBrowserOnWayBar())
