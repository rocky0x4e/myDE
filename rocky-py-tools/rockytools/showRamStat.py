import subprocess as sp
from lib.fuzzel import fuzzel
from lib.notification import DefautNotifier

CC = "Clear mem cache"
memInfo = []
col1 = []
col2 = []
memKb = []
col3 = []
unit = {
    "GB": 1024**2,
    "MB": 1024,
    "KB": 1,
}

notify = DefautNotifier().setAppName("Memory stats").setTransient()


def main():
    fz = fuzzel().makeTable().setPrompt('Memory usage ').setWindowWidth('45ch').setOutputLines(7)
    with open("/proc/meminfo", "r") as f:
        for i in range(6):
            line = f.readline().strip()
            memType, used = line.split(":")
            used = int(used.strip().split(" ")[0])
            memKb.append(used)
            for k, v in unit.items():
                n = used / v
                if n > 1:
                    used = f"{n:.2f} {k}"
                    break
                elif n == 0:
                    used = f"{n:.2f} {k}"
                    k = "null"
                    break
            usedPercent = f"{memKb[-1] * 100 / memKb[0]:.2f}".rstrip('0').rstrip(".").rjust(5)
            fz.addTableLine(line=[memType, str(used), f"{usedPercent}%"], icon='memory')

    fz.addTableLine(line=[CC], icon="broom")
    fz.fmtTable(' | ')
    select = fz.run()

    if select == CC:
        notify.setTitle("Memory clean up").setMessage("Clearing pagecache, dentries, and inodes...").flash()
        sp.call(['sync'])
        sp.run(["sudo", "tee", "/proc/sys/vm/drop_caches"], input="3".encode())
        notify.setMessage("Memory cache cleared").flash(replace=True)
