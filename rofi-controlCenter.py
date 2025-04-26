#!/usr/bin/env python3

import subprocess as sp
from pathlib import Path

import psutil

PROMPT = "System Control"
I = '\\x00icon\\x1f'
W = ""
SEP = f"--------------------------------{I}zigzag"

SCREENLOCK = "xAutolock: OFF"
SCREENLOCK_IC = "unprotected"
for item in psutil.process_iter(['name']):
    if item.info['name'] == "xautolock":
        SCREENLOCK = "xAutolock: ON"
        SCREENLOCK_IC = "secure"
        break

AUTOSLEEP = "Auto sleep: ON";
AUTOSLEEP_IC = "auto-sleep-on"
AUTOSLEEP_TOGGLE = ["systemctl", "--user", "stop Idle.timer"]
timerStt = sp.check_output(["systemctl", "--user", "status", "Idle.timer"]).decode().strip().splitlines()
if "Active: active" in timerStt[3]:
    AUTOSLEEP = "Auto sleep: OFF"
    AUTOSLEEP_IC = "green-tea"
    AUTOSLEEP_TOGGLE = ["systemctl", "--user", "start Idle.timer"]

mitmMenu = "Stop MITM" if sp.run(["tmuxControl.sh", "check", "mitmweb"]).returncode == 0 else "Start MITM"
appiumMenu = "Stop Appium" if sp.run(["tmuxControl.sh", "check", "appium"]).returncode == 0 else "Start Appium"
uxplayMenu = "Stop UxPlay" if sp.run(["tmuxControl.sh", "check", "uxplay"]).returncode == 0 else "Start UxPlay"


def listAppImg():
    appPath = Path.home() / "programs"
    return [{"name": item.name, "cmd": [str(item.absolute())], "icon": "app"}
            for item in appPath.iterdir() if item.name.endswith('.AppImage')]


class ControlCenter:
    CONTROLERS = [
        {"name": f"{W} Shutdown", "icon": "system-shutdown",
         "cmd": ["systemctl", "poweroff"]},
        {"name": f"{W} Reboot", "icon": "system-reboot",
         "cmd": ["systemctl", "reboot"]},
        {"name": f"{W} Logout", "icon": "system-log-out",
         "cmd": ["i3-msg", "exit"]},
        {"name": "Suspend", "icon": "system-suspend",
         "cmd": ["systemctl", "suspend"]},
        {"name": "Lock", "icon": "system-lock-screen",
         "cmd": [str(Path.home() / ".config/i3/scripts/i3lock.sh"), "locker"]},
        {"name": SCREENLOCK, "icon": SCREENLOCK_IC,
         "cmd": ["/home/rocky/.config/i3/scripts/i3lock.sh", "toggle"]},
        {"name": AUTOSLEEP, "icon": AUTOSLEEP_IC,
         "cmd": AUTOSLEEP_TOGGLE},
        {"name": "DNS SEC >>", "icon": "ethernet",
         "cmd": ["rofi-dnssec.sh"]},
        {"name": SEP, 'icon': 'zig-zag'},
        {"name": "HF builds", "icon": "apk-64",
         "cmd": ['rofi-apkInstaller.sh', str(Path.home() / 'HF-data/builds')]},
        {"name": "Restmail", "icon": "email",
         "cmd": ["restmail.py"]},
        {"name": "Pixel 6a", "icon": "smartphone",
         "cmd": ["emulator", "@Pixel_6a_API_33", "-feature", "-Vulkan", "-restart-when-stalled"]},
        {"name": "Pixel 7pro", "icon": "smartphone",
         "cmd": ["emulator", "@Pixel_7_Pro_API_35", "-feature", "-Vulkan", "-restart-when-stalled"]},
        {"name": "AWS VPN", "icon": "VPN",
         "cmd": ["bash", "-c", r"""if ! i3-msg '[class="AWS VPN Client"]' focus; then
                        dex /usr/share/applications/awsvpnclient.desktop; fi """]},
        {"name": mitmMenu, "icon": "hacker-activity",
         "cmd": ["tmuxControl.sh", "toggle", "mitmweb"]},
        {"name": appiumMenu, "icon": "appium",
         "cmd": ["tmuxControl.sh", "toggle", "appium"]},
        {"name": uxplayMenu, "icon": "airplay",
         "cmd": ["tmuxControl.sh", "choose", "uxplay -a -nc -reg -nohold -reset 1"]},
        {"name": SEP, 'icon': 'zig-zag'},
        {"name": "Screen recorder", "icon": "recording",
         "cmd": ["dex", "/usr/share/applications/simplescreenrecorder.desktop"]},
        {"name": "Window inspector", "icon": "inspection",
         "cmd": ['bash', '-c', r'''output=$(xprop | grep "WM_NAME\|WM_CLASS\|ROLE\|WINDOW_TYPE")
            yad --text-info --title="Window Properties" \
            --window-icon=stock_search \
            --width=1000 --height=300 \
            --wrap --center --button=Close:1 --editable=false <<< "$output" ''']},
        {"name": "External monitor", "icon": 'display-settings',
         "cmd": ["rofi-monitor.py"]},
        *listAppImg()
    ]

    def makeRofi(self):
        menu = []
        for item in ControlCenter.CONTROLERS:
            menu.append(f"{item['name']}{I}{item['icon']}")

        echo = sp.Popen(["echo", "-en", '\n'.join(menu)], stdout=sp.PIPE, stderr=sp.PIPE)
        selected = sp.check_output(['rofi', '-dmenu', '-i', '-theme', "overlays/thin-side-bar",
                                    '-icon-theme', 'rofi', '-p', PROMPT, '-select', 'Suspend'],
                                   stdin=echo.stdout).decode().strip()
        if selected.startswith(W):
            echo = sp.Popen(["echo", "-en", f"Yes{I}yes\nNo{I}no"], stdout=sp.PIPE, stderr=sp.PIPE)
            confirm = sp.check_output(['rofi', '-dmenu', '-theme', "overlays/center-yes-no",
                                       '-icon-theme', 'rofi', '-p', "Are you sure?"],
                                      stdin=echo.stdout).decode().strip()
            if confirm == 'No': exit(0)
        return selected

    def find(self, name):
        for item in ControlCenter.CONTROLERS:
            if item['name'] == name:
                return item
        return {}

    def run(self, name):
        cmd = self.find(name).get('cmd')
        if cmd:
            sp.Popen(cmd)


if __name__ == "__main__":
    cc = ControlCenter()
    select = cc.makeRofi()
    cc.run(select)
