import subprocess as sp


class rofi:
    def __init__(self, *args):
        self.args = list(args)
        self.items = []

    def makeDmenu(self):
        self.items = []
        self.args.extend(["-dmenu", "-icon-theme", "rofi", "-i"])
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
        self.args.extend(["-dmenu", "-icon-theme", "rofi", "-i"])
        self.items = [[] for i in range(numOfCol)]
        return self

    def addTableItem(self, item, icon=None, column=0):
        self.items[column].append(f"{item}{self.rofiIcon(icon)}")
        return self

    def rJustifyCol(self, col):
        maxChar = max([len(x) for x in self.items[col]])
        self.items[col] = [x.rjust(maxChar) for x in self.items[col]]
        return self

    def run(self, args=None, addArgs=None):
        addArgs = [] if addArgs is None else addArgs
        try:
            menu = "\n".join(self.items)
        except TypeError:
            items = []
            for col in self.items:
                items.extend(col)
            menu = "\n".join(items)
            colNum = str(len(self.items))
            lineNum = str(max([len(x) for x in self.items]))
            addArgs.extend(['-theme+listview+columns', colNum, '-theme+listview+lines', lineNum,])

        echo = sp.Popen(["echo", "-en", menu], stdout=sp.PIPE, stderr=sp.PIPE)
        if not args:
            args = self.args
        try:
            return sp.check_output(["rofi", *args, *addArgs], stdin=echo.stdout).decode().strip()
        except sp.CalledProcessError:
            exit(0)

    def rofiIcon(self, iconName):
        return f"\\x00icon\\x1f{iconName}" if iconName else ""

    def yesNo(self, msg="Are you sure?"):
        rofiYesNo = rofi('-theme', "overlays/center-yes-no", '-p', msg)
        rofiYesNo.makeDmenu()
        return rofiYesNo.addItem("Yes", "yes").addItem("No", "no").run()

    def isMenuEmpty(self):
        return len(self.items) == 0
