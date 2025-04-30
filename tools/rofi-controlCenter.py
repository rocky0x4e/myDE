#!/usr/bin/env python3

import subprocess as sp
from pathlib import Path

import psutil

PROMPT = "System Control"
I = '\\x00icon\\x1f'
W = ""
SEP = f"--------------------------------{I}zigzag"
H = Path.home()
autolockStt = False
for item in psutil.process_iter(['name']):
    if item.info['name'] == "xautolock":
        autolockStt = True
        break

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
         "cmd": [f"{H}/.config/i3/scripts/i3lock.sh", "locker"]},
        {
            True: {"name": "XAutolock: ON", "icon": "secure", "cmd": [f"{H}/.config/i3/scripts/i3lock.sh", "toggle"]},
            False:{"name": "XAutolock: OFF", "icon": "unprotected", "cmd": [f"{H}/.config/i3/scripts/i3lock.sh", "toggle"]}
        }[autolockStt],
        {
            True:  {'name':"Auto sleep: ON", "icon":"auto-sleep-on", "cmd":["systemctl", "--user", "stop", "Idle.timer"]},
            False: {'name':"Auto sleep: OFF", "icon":"green-tea", "cmd":["systemctl", "--user", "start", "Idle.timer"]}
        }[sp.run(["systemctl", "--user", "is-active", "Idle.timer"]).returncode == 0],
        {"name": "Cinnamon settings", "icon":"gnome-settings",
         "cmd":['cinnamon-settings']},
        {"name": "Theme settings", "icon":"cinnamon-preferences-color",
         "cmd":['cinnamon-settings', 'themes']},
        {"name": SEP, 'icon': 'zig-zag'},
        {"name": "HF builds", "icon": "apk-64",
         "cmd": ['rofi-apkInstaller.sh', f'{H}/HF-data/builds']},
        {"name": "Restmail", "icon": "email",
         "cmd": ["restmail.py"]},
        {"name": "Pixel 6a", "icon": "smartphone",
         "cmd": ["emulator", "@Pixel_6a_API_33", "-feature", "-Vulkan", "-restart-when-stalled"]},
        {"name": "Pixel 7pro", "icon": "smartphone",
         "cmd": ["emulator", "@Pixel_7_Pro_API_35", "-feature", "-Vulkan", "-restart-when-stalled"]},
        {"name": "AWS VPN", "icon": "VPN",
         "cmd": ["bash", "-c", r"""if ! i3-msg '[class="AWS VPN Client"]' focus; then
                        dex /usr/share/applications/awsvpnclient.desktop; fi """]},
        {
            True:  {"name": "Stop MITM", "icon": "hacker-activity","cmd": ["tmuxControl.sh", "toggle", "mitmweb"]},
            False: {"name": "Start MITM", "icon": "hacker-activity","cmd": ["tmuxControl.sh", "toggle", "mitmweb"]}
        }[sp.run(["tmuxControl.sh", "check", "mitmweb"]).returncode == 0],
        {
            True:  {"name": "Stop Apppium", "icon": "appium", "cmd": ["tmuxControl.sh", "toggle", "appium"]},
            False: {"name": "Start Apppium", "icon": "appium", "cmd": ["tmuxControl.sh", "toggle", "appium"]}
        }[sp.run(["tmuxControl.sh", "check", "appium"]).returncode == 0],
        {
            True:  {"name": "Stop UxPlay", "icon": "airplay","cmd": ["tmuxControl.sh", "choose", "uxplay -a -nc -reg -nohold -reset 1"]},
            False: {"name": "Start UxPlay", "icon": "airplay","cmd": ["tmuxControl.sh", "choose", "uxplay -a -nc -reg -nohold -reset 1"]}
        }[sp.run(["tmuxControl.sh", "check", "uxplay"]).returncode == 0],
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
