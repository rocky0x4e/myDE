#!/usr/bin/env python3

import subprocess as sp
import json
import sys


browsers = {
    "brave-browser.desktop": {
        "xdgName": "brave-browser.desktop",
        "name": "Brave",
        "app-id": "brave-browser",
    },
    "google-chrome.desktop": {
        "xdgName": "google-chrome.desktop",
        "name": "Chrome",
        "app-id": "Google-chrome",
    },
    "firefox.desktop": {
        "xdgName": "firefox.desktop",
        "name": "Firefox",
        "app-id": "firefox",
    }
}
unknow = {
    "xdgName": "",
    "name": "Unknown",
    "app-id": "",
}
DEX_DIR = "/usr/share/applications"


def findByName(name):
    for o in browsers.values():
        if name == o['name']:
            return o
    return {}


def getCurrentBrowser():
    return sp.run(["xdg-settings", "get", "default-web-browser"], capture_output=True, text=True).stdout.strip()


def show():
    print(json.dumps({"class": browsers.get(getCurrentBrowser(), unknow)["name"],
                      "tooltip": "Click: cycle/open browser \nRight click: open other browser\nMiddle click: change default browser"}))


def open(name=''):
    if not name:
        curr = browsers.get(getCurrentBrowser(), unknow)
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
    curr = browsers.get(getCurrentBrowser(), unknow)
    fz = fuzzel({'--select': curr['name']}).makeDmenu().setAnchor("top").setMesg("Open browser ").hidePrompt()
    for k, o in browsers.items():
        fz.addItem(o['name'], o['name'])
    select = fz.run()
    open(select)


def changeDefault():
    from lib.fuzzel import fuzzel
    curr = browsers.get(getCurrentBrowser(), unknow)
    fz = fuzzel({'--select': curr['name']}).makeDmenu().setAnchor("top").setMesg("Select default browser ").hidePrompt()
    for k, o in browsers.items():
        fz.addItem(o['name'], o['name'])
    select = fz.run()
    newBr = findByName(select)['xdgName']
    sp.call(["xdg-settings", "set", "default-web-browser", newBr])


ACTION = sys.argv[1]
if ACTION == "show":
    show()
elif ACTION == "change":
    changeDefault()
elif ACTION == "open":
    open()
elif ACTION == "select":
    selectOpen()
