#!/usr/bin/env python3

import sys
import os
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess as sp

class DataHelper:
    DATA_DIR = f'{os.getenv("HOME")}/.config/polybar/data'

    @staticmethod
    def isFile(filename):
        return os.path.isfile(f"{DataHelper.DATA_DIR}/{filename}")

    @staticmethod
    def list(folder=""):
        return os.listdir(f"{DataHelper.DATA_DIR}/{folder}")

    def getAbsPath(self):
        return f"{self.__class__.DATA_DIR}/{self.fileName}"

    def __init__(self, name, lock=False) -> None:
        self.fileName = name
        self.fileLock = f"{name}.lock"
        self.fileFull = f"{self.__class__.DATA_DIR}/{self.fileName}"
        self.lockFull = f"{self.fileFull}.lock"
        self.needLock = lock

    def readJsonFile(self):
        self.getLock()
        try:
            with open(self.fileFull, "r") as f:
                import json
                data = json.load(f)
        except:
            data = {}
        self.unlock()
        return data

    def writeJsonFile(self, data={}):
        self.getLock()
        with open(self.fileFull, "w+") as f:
            import json
            json.dump(data, f, indent=3)
        self.unlock()

    def getLock(self):
        if not self.needLock:
            return
        if os.path.isfile(self.lockFull):
            exit(0)
        with open(self.lockFull, "w+"):
            pass

    def unlock(self):
        if not self.needLock:
            return
        if os.path.isfile(self.lockFull):
            os.remove(self.lockFull)

    def remove(self):
        os.remove(self.fileFull)


def doPlot(fileName):
    DATA = DataHelper(fileName).readJsonFile()["history"]
    hours = []
    percent = []
    fig, ax = plt.subplots(layout='constrained')
    dates = sorted(DATA.keys())
    first_day = dates[0]

    for day in dates:
        hour = (datetime.fromisoformat(day.rstrip("Z")) - datetime.fromisoformat(first_day.rstrip("Z")))\
            .total_seconds()/3600
        hours.append(hour)
        p = DATA[day]
        percent.append(p)

    ax.set_xlabel("hours")
    ax.set_ylabel("percent")
    secAx = ax.secondary_xaxis('top', functions=(lambda x: x/24, lambda x: x*24))
    secAx.set_xlabel('days')

    ax.plot(hours, percent)

    def close_figure(event):
        if event.key == 'escape':
            plt.close(event.canvas.figure)

    plt.gcf().canvas.mpl_connect("key_press_event", close_figure)
    plt.title(fileName.split("/")[-1])
    plt.show()


def plotFolder(folder):
    files = DataHelper.list(folder)
    zCheckList=[]
    for f in files:
        zCheckList.append("true")
        zCheckList.append(f)
    files = sp.check_output(["zenity", "--list", "--title", "Plotter", "--width=500", "--height=400",
             "--checklist", "--text=Select data to plot", "--hide-header",
             "--column=null", "--column=Files", *zCheckList]).decode().strip().split("|")

    helpers = [DataHelper(f"{folder}/{file}") for file in files if file.endswith(".json")]
    allData = {dh.fileName.split("/")[-1].rstrip(".json"): dh.readJsonFile().get("history",{}) for dh in helpers}
    eachMin = [min(d.keys()) for d in allData.values() if d.values()]
    minDate = min(eachMin)
    graphs = {}

    # cal data for each graph
    for file, data in allData.items():
        dates = sorted(data.keys())
        hours = []
        percents = []
        for day in dates:
            hour = (datetime.fromisoformat(day.rstrip("Z")) - datetime.fromisoformat(minDate.rstrip("Z")))\
                .total_seconds()/3600
            hours.append(hour)
            percents.append(data[day])
        graphs[file] = [hours, percents]

    # plot
    fig, ax = plt.subplots(layout='constrained')
    ax.set_xlabel("hours")
    ax.set_ylabel("percent")
    secAx = ax.secondary_xaxis('top', functions=(lambda x: x/24, lambda x: x*24))
    secAx.set_xlabel('days')
    lines = []
    for name, data in graphs.items():
        l = ax.plot(*data, label=name, picker=True, pickradius=10)
        lines.append(l[-1])

    def close_figure(event):
        if event.key == 'escape':
            plt.close(event.canvas.figure)

    def onpick(event):
        leg_line = event.artist
        orig_line = lined[leg_line]
        vis = not orig_line.get_visible()
        orig_line.set_visible(vis)
        if vis:
            leg_line.set_alpha(1.0)
        else:
            leg_line.set_alpha(0.15)
        fig.canvas.draw()

    plt.title("UPower")
    legends = ax.legend(fancybox=True, shadow=True)
    lined = {oline: lline for lline, oline in zip(legends.get_lines(), lines)}
    fig.canvas.mpl_connect("key_press_event", close_figure)
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()


if __name__ == "__main__":
    if DataHelper.isFile(sys.argv[1]):
        doPlot(sys.argv[1])
    else:
        plotFolder(sys.argv[1])
