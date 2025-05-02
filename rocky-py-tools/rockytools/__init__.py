import subprocess as sp
import json


class rofi:
    def __init__(self, *args):
        self.args = list(args)
        self.items = []
        self.defaultArgs = ["-dmenu", "-icon-theme", "rofi", "-i"]

    def newMenu(self):
        self.items = []
        return self

    def sortMenu(self, reverse=False):
        self.items = sorted(self.items, reverse=reverse)
        return self

    def addItem(self, item, icon=None, index=-1):
        if icon:
            item = f"{item}{self.rofiIcon(icon)}"
        if index == -1:
            self.items.append(item)
            return self
        self.items.insert(index, item)
        return self

    def makeTable(self, numOfCol):
        self.items = []
        for i in range(numOfCol):
            self.items.append([])
        return self

    def addTableItem(self, item, icon=None, column=0):
        self.items[column].append(f"{item}{self.rofiIcon(icon)}")
        return self

    def rJustifyCol(self, col):
        maxChar = max([len(x) for x in self.items[col]])
        self.items[col] = [x.rjust(maxChar) for x in self.items[col]]
        return self

    def run(self, args=None, addArgs=None):
        try:
            menu = "\n".join(self.items)
        except TypeError:
            items = []
            for col in self.items:
                for item in col:
                    items.append(item)
            menu = "\n".join(items)

        echo = sp.Popen(["echo", "-en", menu], stdout=sp.PIPE, stderr=sp.PIPE)
        if not args:
            args = self.args
        for arg in self.defaultArgs:
            if arg not in args:
                args.append(arg)
        addArgs = [] if addArgs is None else addArgs
        try:
            return sp.check_output(["rofi", *args, *addArgs], stdin=echo.stdout).decode().strip()
        except sp.CalledProcessError:
            exit(0)

    def rofiIcon(self, iconName):
        return f"\\x00icon\\x1f{iconName}" if iconName else ""

    def yesNo(self, msg):
        self.newMenu()
        args = ['-dmenu', '-theme', "overlays/center-yes-no",
                '-icon-theme', 'rofi', '-p', "Are you sure?"]
        return self.addItem("Yes", "yes").addItem("No", "no").run(args)

    def isMenuEmpty():
        return len(self.items) == 0
