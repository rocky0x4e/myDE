#!/usr/bin/env python3

import sys
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess as sp
import json

from pathlib import Path

DATA_DIR = Path.home() / ".config" / "polybar" / "data"


def plotAFile(file: Path):
    DATA = json.looads(file.read_text())["history"]
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
    plt.title(file.name)
    plt.show()


def plotFolder(folder):
    files = [f for f in folder.iterdir()]
    names = [f.name for f in files]
    zCheckList = []
    for n in names:
        zCheckList.append("false")
        zCheckList.append(n)
    while True:
        selector = sp.Popen(["yad", "--list", "--title", "Plotter", "--width=500", "--height=400",
                            "--checklist", "--text=Select data to plot", "--no-headers",
                             "--column=null", "--column=Files",
                             "--button=Select all:3", "--button=Select none:5", "--button=Cancel:1", "--button=OK:0",
                             *zCheckList], stdout=sp.PIPE)
        returnCode = selector.wait()
        if returnCode == 0:
            break
        if returnCode in [1, 252]:
            return
        toggle = {3: 'true', 5: 'false'}
        for i in range(len(zCheckList)):
            zCheckList[i] = toggle[returnCode] if zCheckList[i] in ['true', 'false'] else zCheckList[i]
    stdout, stderr = selector.communicate()

    selectedFiles = stdout.decode().split("|")

    selectedFiles = [f for f in files if f.name in selectedFiles]
    allData = {f.name.rstrip(".json"): json.loads(f.read_text()).get("history", {}) for f in selectedFiles}
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
    path = Path(sys.argv[1])
    path = path if path.exists() else DATA_DIR / path

    if path.is_file():
        plotAFile(path)
    elif path.is_dir():
        plotFolder(path)
