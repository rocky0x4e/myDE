#!/usr/bin/env python3

import subprocess as sp
import re


I = "\\x00icon\\x1f"

class XDisplay:
    def __init__(self, data):
        print(data)
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
                currentSettings =line0splitted[3].split("+")
            else:
                currentSettings =line0splitted[2].split("+")
            print(currentSettings)
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
        self.screenData = data[0]
        self.xdisplays  = []
        newScreen = []
        for line in data[1:]:
            if re.match(r"[a-zA-Z]", line):
                if newScreen:
                    self.xdisplays.append(XDisplay(newScreen))
                newScreen = [line]
            elif line.startswith(' '):
                newScreen.append(line)
        if newScreen: # add the last one
            self.xdisplays.append(XDisplay(newScreen))
        self.primaryDisplay = None
        for d in self.xdisplays:
            if d.isPrimary:
                self.primaryDisplay = d

    def __makeRofi(self, menu):
        echo = sp.Popen(["echo", "-e", '\n'.join(menu)],stdout=sp.PIPE,stderr=sp.PIPE)
        return sp.check_output(['rofi', '-dmenu', '-theme', 'overlays/thin-side-bar',
                                  '-icon-theme', 'rofi'], stdin=echo.stdout).decode().strip()

    def rofiList(self):
        menu = []
        for disp in self.xdisplays:
            if disp.isConnected:
                icon="screen-active" if disp.isActive else "screen-inactive"
                menu.append(f"{disp.name}{I}{icon}")
        menu.append(f"Arandr{I}display-settings")
        return self.__makeRofi(menu)


    def findDisplay(self, name):
        for d in self.xdisplays:
            if d.name == name:
                return d

    def toggleDisplay(self, display, *args):
        if display.isActive:
            sp.Popen(["xrandr", "--output", display.name, "--off"])
        else:
            sp.Popen(["xrandr", "--output", display.name, "--auto", "--left-of", self.primaryDisplay.name, *args])

xrandr = XRandR()
select = xrandr.rofiList()
if select == "Arandr":
    sp.Popen(["arandr"])
else:
    display = xrandr.findDisplay(select)
    xrandr.toggleDisplay(display,'--rotate', 'left')