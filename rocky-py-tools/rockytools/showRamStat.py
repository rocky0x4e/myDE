import subprocess as sp
from rockytools import rofi


CC = "Clear mem cache"
memInfo = []
col1 = []
col2 = []
memKb = []
col3 = []
unit = {
    "GB2": 1024**2,
    "MB4": 1024,
    "KB2": 1,
}


def main():
    rf = rofi('-theme', 'overlays/center-dialog',
              '-theme+listview+columns', '3', '-theme+listview+lines', '7',
              '-theme+window+width', f'70ch',
              '-p', 'Memory usage', '-theme+inputbar+children', '[ prompt ]')
    rf.makeTable(3)
    with open("/proc/meminfo", "r") as f:
        for i in range(6):
            line = f.readline().strip()
            memType, used = line.split(":")
            used = int(used.strip().split(" ")[0])
            memKb.append(used)
            for k, v in unit.items():
                n = used / v
                if n > 1:
                    used = f"{n:.2f}"
                    break
                elif n == 0:
                    used = f"{n}{I}null"
                    break
            usedPercent = f"{memKb[-1] * 100 / memKb[0]:.2f}".rstrip('0').rstrip(".").rjust(5)
            rf.addTableItem(memType, "memory", 0)
            rf.addTableItem(str(used), k, 1)
            rf.addTableItem(f"{usedPercent}%", "pie-chart", 2)
    rf.rJustifyCol(1)
    rf.addTableItem(CC, "broom", 0)
    rf.addTableItem("", column=1)
    rf.addTableItem("", column=2)
    select = rf.run()

    if select == CC:
        sp.Popen(["clearRamCache.sh"])
