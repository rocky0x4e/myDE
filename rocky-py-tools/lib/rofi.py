import subprocess as sp


class rofi:
    def __init__(self, kwargs=None):
        self.kwargs = kwargs if kwargs else {}
        self.items = []

    def makeDmenu(self):
        self.items = []
        self.kwargs['-dmenu'] = ""
        self.kwargs["-icon-theme"] = "rofi"
        self.kwargs['-i'] = ""
        self.kwargs['-markup'] = ""
        return self

    def setInputBarChildren(self, childrend):
        self.kwargs["-theme+inputbar+children"] = childrend
        return self

    def setTheme(self, theme):
        self.kwargs["-theme"] = theme
        return self

    def setIconTheme(self, iconTheme):
        self.kwargs["-icon-theme"] = iconTheme
        return self

    def setPrompt(self, prompt):
        self.kwargs["-p"] = prompt
        return self

    def setWindowWidth(self, windowWidth):
        self.kwargs["-theme+window+width"] = windowWidth
        return self

    def sortDmenu(self, reverse=False):
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
        self.kwargs['-dmenu'] = ""
        self.kwargs["-icon-theme"] = "rofi"
        self.kwargs['-i'] = ""
        self.items = [[] for i in range(numOfCol)]
        return self

    def addTableItem(self, item, icon=None, column=0):
        self.items[column].append(f"{item}{self.rofiIcon(icon)}")
        return self

    def addPseudoTableIcon(self, icon):
        self.items[-1][-1] += self.rofiIcon(icon)

    def fmtPseudoTable(self):
        try:
            colWidth = [max([len(item) for item in col]) for col in self.items]
        except ValueError:
            return self
        newItemList = []
        for lineIndex in range(len(self.items[0])):
            item = ''
            for colIndex in range(len(self.items)):
                item += self.items[colIndex][lineIndex].ljust(colWidth[colIndex]) + " |  "
            newItemList.append(item.strip(" | "))
        self.items = newItemList
        return self

    def rJustifyCol(self, col):
        maxChar = max([len(x) for x in self.items[col]])
        self.items[col] = [x.rjust(maxChar) for x in self.items[col]]
        return self

    def run(self, additionArgs=None):
        additionArgs = {} if additionArgs is None else additionArgs
        try:
            menu = "\n".join(self.items)
        except TypeError:
            items = []
            for col in self.items:
                items.extend(col)
            menu = "\n".join(items)
            colNum = str(len(self.items))
            lineNum = str(max([len(x) for x in self.items]))
            self.kwargs['-theme+listview+columns'] = colNum
            self.kwargs['-theme+listview+lines'] = lineNum

        allKwArgs = {**self.kwargs, **additionArgs}
        allArgs = []
        for k, v in allKwArgs.items():
            allArgs.append(k)
            allArgs.append(v) if v else None

        try:
            # print("debug rofi run\n", ["rofi", *allArgs])
            # print("debug rofi menu\n", menu)
            return sp.check_output(["rofi", *allArgs], input=menu.encode()).decode().strip()
        except sp.CalledProcessError:
            exit(0)

    def rofiIcon(self, iconName):
        return f"\x00icon\x1f{iconName}" if iconName else ""

    def isMenuEmpty(self):
        return len(self.items) == 0 if type(self.items[0]) is not list else self.items[0] == []

    def addSeparator(self, length=40, text='', dash='-', icon="zigzag"):
        self.addItem(*rofi.separator(length, text, dash, icon))
        return self

    def addMesg(self, mesg):
        self.kwargs['-mesg'] = mesg
        return self

    @staticmethod
    def separator(length=40, text='', dash='-', icon="zigzag"):
        if text:
            l = len(text)
            odd = l % 2 == 1
            dashCount = int((length - l)/2 - 1)
            dashesLeft = f"{dash * dashCount}"
            dashesRight = dashesLeft + dash if odd else dashesLeft
            print(f"\n{text}:{odd}\n{dashesLeft}\n{dashesRight}")
            return (f"{dashesLeft} {text} {dashesRight}", "zigzag")
        return dash * length, icon

    @staticmethod
    def yesNo(msg="Are you sure?"):
        rofiYesNo = rofi().makeDmenu().setTheme("overlays/center-yes-no").setPrompt(msg)
        return rofiYesNo.addItem("Yes", "yes").addItem("No", "no").run()
