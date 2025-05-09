#!/usr/bin/env python3

from pathlib import Path
import subprocess as sp
import sys
import os

INSTALL = [
    {
        "msg": "Installing configs...",
        "from": "config",
        "to": ".config",
    },
    {
        "msg": "Installing bash tools...",
        "from": "tools",
        "to": ".local/bin/",
    },
    {
        "msg": "Installing icons...",
        "from": "icons",
        "to": ".local/share/icons/",
    },
]


def backup(folder: Path):
    if folder.is_symlink():
        folder.unlink()
    else:
        folder.rename(f"{folder.absolute()}.bk")


def installResources():
    while True:
        installPrompt = f"{"="*80}\n0 : All below\n"
        for i in range(len(INSTALL)):
            msg = INSTALL[i]['msg']
            installPrompt += f"{i+1} : {msg}\n"
        installPrompt += "Choose what to install, enter anything to exist: "

        select = input(installPrompt).strip()
        try:
            if int(select) < 0 or int(select) > len(INSTALL):
                print("Quit !!!")
                return
        except:
            print("Quit !!!")
            return

        if select == "0":
            installQ = range(len(INSTALL))
        else:
            installQ = [int(select)-1]
        for i in installQ:
            D = INSTALL[i]
            print(D['msg'])

            fromPath = Path(D["from"])
            for item in fromPath.iterdir():
                toPath = Path.home() / f"{D['to']}/{item.name}"
                print(f"{toPath.absolute()} -> {fromPath.absolute()}/{item.name}")
                backup(toPath)
                toPath.symlink_to(fromPath.absolute() / item.name)
        input("Press Enter to continue.")


def installBinary():
    print("Installing the cli commands")
    sp.check_call(
        [sys.executable, "-m", "pip", "install", "-e", ".", "--force", "--break-system-packages",],
        cwd="rocky-py-tools"  # 👈 this sets the working directory
    )


def installSudoerMod():
    input("!!! Installing sudoer mods, need root access to install, Enter to continue.\n"
          "Hit Ctrl + C to skip it but the clear ram script and the MMC refresh function won't work:\n")
    sudoerConf = (f"{os.environ["USER"]} ALL=(ALL) NOPASSWD: /sbin/modprobe\n"
                  f"{os.environ["USER"]} ALL=(ALL) NOPASSWD: /usr/bin/tee /proc/sys/vm/drop_caches\n")
    sp.run(
        ['sudo', 'tee', '/etc/sudoers.d/myDE'],
        input=sudoerConf.encode()
    )


installResources()
installBinary()
installSudoerMod()
