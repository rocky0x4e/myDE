#!/usr/bin/env python3

import subprocess as sp
import json
import sys
import os


HOME = os.getenv("HOME")
TOOLTIP = "Click: cycle/open browser\nRight click: open other browser\nMiddle click: change default browser"

BROWSERS = {
    "brave-browser.desktop": {
        "xdgName": "brave-browser.desktop",
        "name": "Brave",
        "app-id": "brave-browser",
        "icon": f"{HOME}/.local/share/icons/wmicons/512x512/apps/Brave.png"
    },
    "google-chrome.desktop": {
        "xdgName": "google-chrome.desktop",
        "name": "Chrome",
        "app-id": "Google-chrome",
        "icon": f"{HOME}/.local/share/icons/wmicons/512x512/apps/Chrome.png"
    },
    "firefox.desktop": {
        "xdgName": "firefox.desktop",
        "name": "Firefox",
        "app-id": "firefox",
        "icon": f"{HOME}/.local/share/icons/wmicons/512x512/apps/Firefox.png"
    }
}
unknow = {
    "xdgName": "",
    "name": "Unknown",
    "app-id": "",
    "icon": f"{HOME}/.local/share/icons/wmicons/512x512/apps/shrug.png"
}
DEX_DIR = "/usr/share/applications"


def findByName(name):
    for o in BROWSERS.values():
        if name == o['name']:
            return o
    return {}


def getCurrentBrowser():
    xdgCB = sp.run(["xdg-settings", "get", "default-web-browser"], capture_output=True, text=True).stdout.strip()
    return BROWSERS.get(xdgCB, unknow)


def show():
    curr = getCurrentBrowser()
    print(json.dumps({"class": curr["name"], "tooltip": TOOLTIP}))


def showIcon():
    curr = getCurrentBrowser()
    print(json.dumps([{"path": curr["icon"], "marker": "normal", "tooltip": TOOLTIP}]))


def open(name=''):
    if not name:
        curr = getCurrentBrowser()
    else:
        curr = findByName(name)

    appId = curr['app-id']
    from lib.niri import niriwm
    windows = sorted(niriwm.getWindows().findWindows(appid=appId), key=lambda k: k.id)
    count = len(windows)
    if not windows:
        sp.call(["dex", f"{DEX_DIR}/{curr['xdgName']}"])
        return
    for i in range(count):
        if windows[i].isFocused:
            niriwm.focusWindow(windows[i - 1])
            return
    niriwm.focusWindow(windows[0])


def selectOpen():
    from lib.fuzzel import fuzzel
    curr = getCurrentBrowser()
    fz = fuzzel({'--select': curr['name']}).makeDmenu().setAnchor("top").setMesg("Open browser ").hidePrompt()
    for k, o in BROWSERS.items():
        fz.addItem(o['name'], o['name'])
    select = fz.run()
    open(select)


def changeDefault():
    from lib.fuzzel import fuzzel
    curr = getCurrentBrowser()
    fz = fuzzel({'--select': curr['name']}).makeDmenu().setAnchor("top").setMesg("Select default browser ").hidePrompt()
    for k, o in BROWSERS.items():
        fz.addItem(o['name'], o['name'])
    select = fz.run()
    newBr = findByName(select)['xdgName']
    sp.check_call(["xdg-settings", "set", "default-web-browser", newBr])


ACTION = sys.argv[1]
if ACTION == "show":
    show()
elif ACTION == "showIcon":
    showIcon()
elif ACTION == "change":
    changeDefault()
elif ACTION == "open":
    open()
elif ACTION == "select":
    selectOpen()
sp.call(["pkill", "-n", "waybar", "--signal", "41"])
