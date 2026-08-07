import subprocess as sp
import os


class fuzzel:
    def __init__(self, kwargs=None):
        self.kwargs = kwargs or {}
        self.items = []
        self.table = []
        self.isTable = False
        self.tableRowCount = 0
        self.tableColumn = 0
        self.tableColumnWidth = {}
        self.maxLines = 29

    def setMaxLines(self, lineNum):
        self.maxLines = lineNum
        return self

    def setOutputLines(self, lineNum):
        self.kwargs['--lines'] = f'{lineNum}'
        return self

    def setAnchor(self, position):
        self.kwargs['--anchor'] = position
        return self

    def makeDmenu(self):
        self.items = []
        self.kwargs['--dmenu'] = ""
        self.kwargs["--icon-theme"] = "wmicons"
        return self

    def unsetIconTheme(self):
        try:
            del (self.kwargs["--icon-theme"])
        except KeyError:
            pass
        return self

    def makeTable(self):
        self.makeDmenu()
        self.isTable = True
        return self

    def addTableRow(self, **kwargs):
        """ Add a row to the table
        Params:
            @row: a list of items in the row
            @icon: icon of the row

        Returns:
            _type_: _description_
        """
        if not self.isTable:
            raise RuntimeError(
                "Object does not support table format, "
                "use 'makeTabke' method first to create a table menu")
        row = kwargs['row'] = [f'{c}' for c in kwargs.get('row', [])]
        self.table.append(kwargs)
        self.tableRowCount += 1
        self.tableColumn = len(row) if len(row) > self.tableColumn else self.tableColumn
        for i in range(len(row)):
            if len(row[i]) > self.tableColumnWidth.get(i, 0):
                self.tableColumnWidth[i] = len(row[i])

        return self

    def fmtTable(self, colSeparator="〱"):
        for item in self.table:
            row, icon = item['row'], item.get('icon', '')
            fmtRow = [row[i].ljust(self.tableColumnWidth[i]) for i in range(len(row))]
            self.items.append(colSeparator.join(fmtRow) + f"\x00icon\x1f{icon}")
        return self

    def setIconTheme(self, iconTheme=''):
        if iconTheme:
            self.kwargs["--icon-theme"] = iconTheme
        else:
            del (self.kwargs["--icon-theme"])
        return self

    def setPrompt(self, prompt):
        self.kwargs["-p"] = prompt
        return self

    def hidePrompt(self):
        self.kwargs['--hide-prompt'] = ''
        return self

    def onlyPrompt(self):
        self.kwargs['--prompt-only'] = ''
        return self

    def setMesg(self, mesg):
        self.kwargs['--mesg'] = mesg
        return self

    def setWindowWidth(self, windowWidth):
        windowWidth = str(windowWidth)
        self.kwargs["-w"] = windowWidth + "ch" if not windowWidth.endswith('ch') else windowWidth
        return self

    def sortDmenu(self, reverse=False):
        self.items = sorted(self.items, reverse=reverse)
        return self

    def setSelectIdx(self, index):
        self.kwargs['--select-index'] = str(index)
        return self

    def addItem(self, item, icon=None, index=-1):
        if icon:
            item = f"{item}\x00icon\x1f{icon}" if icon else item
        if index == -1:
            self.items.append(item)  # type: ignore
            return self
        self.items.insert(index, item)  # type: ignore
        return self

    def run(self, additionArgs=None):
        additionArgs = {} if additionArgs is None else additionArgs
        lineCount = min(len(self.items), self.maxLines)

        menu = "\n".join(self.items)  # type: ignore

        allKwArgs = {"--lines": str(lineCount), **self.kwargs, **additionArgs}
        allArgs = []
        allArgs = [item for pair in allKwArgs.items() for item in pair if item] + os.getenv("OPTIONS", "").split(' ')
        try:
            return sp.check_output(["fuzzel", *allArgs], input=menu.encode()).decode().strip()
        except sp.CalledProcessError as e:
            print(":::::: ERROR :::::\n", e)
            exit(0)

    def isMenuEmpty(self):
        return self.items == [] or self.items[0] == []

    def addSeparator(self, length=40, text='', dash='-', icon="zigzag"):
        self.addItem(*fuzzel.separator(length, text, dash, icon))
        return self

    @staticmethod
    def separator(length=40, text='', dash='-', icon="zigzag"):
        if text:
            l = len(text)
            odd = l % 2 == 1
            dashCount = int((length - l)/2 - 1)
            dashesLeft = f"{dash * dashCount}"
            dashesRight = dashesLeft + dash if odd else dashesLeft
            return (f"{dashesLeft} {text} {dashesRight}", "zigzag")
        return dash * length, icon

    @staticmethod
    def yesNo(msg="Are you sure? "):
        return fuzzel().makeDmenu().setMesg(msg).hidePrompt().setOutputLines(3)\
            .addItem("Yes", "yes")\
            .addItem("No", "no").run()
