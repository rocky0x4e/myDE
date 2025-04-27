#!/usr/bin/env python3

import subprocess as sp

I = "\\x00icon\\x1f"
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
with open("/proc/meminfo", "r") as f:
    for i in range(6):
        line = f.readline().strip()
        memType, used = line.split(":")
        used = int(used.strip().split(" ")[0])
        memKb.append(used)
        for k, v in unit.items():
            n = used / v
            if  n > 1 :
                used = f"{n:.2f} {k}"
                break
        usedPercent = f"{memKb[-1] * 100 / memKb[0]:.2f}".rstrip('0').rstrip(".").rjust(5)
        col1.append(f"{memType}{I}memory")
        col2.append(str(used))
        col3.append(f"{usedPercent}%")
maxCharCol2 = max([len(x) for x in col2])
col2 = [x.rjust(maxCharCol2) for x in col2]
col1.append(f"{CC}{I}broom")
col2.append("")
col3.append("")
echo = sp.Popen(["echo", "-en", "\n".join(col1 + col2 + col3)], stdout=sp.PIPE, stderr=sp.PIPE)
try:
    select = sp.check_output(["rofi", '-dmenu', '-icon-theme', 'rofi', '-theme', 'overlays/center-dialog',
                 '-theme+listview+columns', '3', '-theme+listview+lines', '7',
                 '-theme+window+width', f'70ch',
                 '-p', 'Memory usage', '-theme+inputbar+children', '[ prompt ]'], stdin=echo.stdout).decode().strip()
except sp.SubprocessError:
    exit(0)

if select == CC:
    sp.Popen(["clearRamCache.sh"])