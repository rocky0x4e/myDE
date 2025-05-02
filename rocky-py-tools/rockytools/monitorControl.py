import subprocess as sp
import re
from rockytools import rofi


class XDisplay:
    def __init__(self, data):
        self.isActive = False
        self.defaultRes = None
        self.currentRes = None
        self.coordinateX = None
        self.coordinateY = None
        line0splitted = data[0].split(" ")
        self.name = line0splitted[0]
        self.isConnected = line0splitted[1] == "connected"
        self.isPrimary = line0splitted[2] == "primary"
        if self.isActive:
            if self.isPrimary:
                currentSettings = line0splitted[3].split("+")
            else:
                currentSettings = line0splitted[2].split("+")
            self.currentRes = currentSettings[0]
            self.coordinateX = currentSettings[1]
            self.coordinateY = currentSettings[2]
        for line in data[1:]:
            if '+' in line:
                self.defaultRes = line.strip().split(" ")[0]
                break
        for line in data[1:]:
            if "*" in line:
                self.isActive = True
                break


class XRandR:
    def __init__(self):
        data = sp.check_output(['xrandr']).decode().strip().splitlines()
        self.rofi = rofi('-theme', 'overlays/center-dialog', '-p', "Display settings")
        self.screenData = data[0]
        self.displays = []
        displayData = []
        for line in data[1:]:
            if re.match(r"[a-zA-Z]", line):
                if displayData:
                    self.displays.append(XDisplay(displayData))
                displayData = [line]
            elif line.startswith(' '):
                displayData.append(line)
        if displayData:  # add the last one
            self.displays.append(XDisplay(displayData))
        self.primaryDisplay = None
        for d in self.displays:
            if d.isPrimary:
                self.primaryDisplay = d

    def rofiList(self):
        for disp in self.displays:
            if disp.isConnected:
                icon = "screen-active" if disp.isActive else "screen-inactive"
                self.rofi.addItem(disp.name, icon)
        self.rofi.addItem("Arandr", "display-settings")
        return self.rofi.run()

    def findDisplay(self, name):
        for d in self.displays:
            if d.name == name:
                return d

    def toggleDisplay(self, display, *args):
        if display.isActive:
            sp.Popen(["xrandr", "--output", display.name, "--off"])
        else:
            sp.Popen(["xrandr", "--output", display.name, "--auto", "--left-of", self.primaryDisplay.name, *args])


def main():
    xrandr = XRandR()
    select = xrandr.rofiList()
    if select == "Arandr":
        sp.Popen(["arandr"])
    else:
        display = xrandr.findDisplay(select)
        xrandr.toggleDisplay(display, '--rotate', 'left')
