import types
import psutil
from lib.notifysend import NotifySend
from lib.rofi import rofi
from pathlib import Path
import subprocess as sp
import libtmux

W = ""
H = Path.home()
rf = rofi('-i', '-select', 'Suspend').setTheme("overlays/thin-side-bar").setPrompt("System Control")
notify = NotifySend().setAppName("System control").setTransient()
SEP = rf.separator(32)
tmuxServer = libtmux.Server()
tmuxSession = "tmuxControl"


def tmuxHelper(action, command):
    appName = Path(command.split(' ')[0]).name
    try:
        session = tmuxServer.sessions.get(session_name=tmuxSession)
    except:
        session = tmuxServer.new_session(session_name=tmuxSession)
    try:
        window = session.windows.get(window_name=appName)
    except:
        window = session.new_window(window_name=appName)
    pane = window.panes.get()
    match action:
        case "start":
            pane.send_keys(command)
            notify.setTitle("Tmux app control").setMessage(f"{appName} started in {window}").flash()
        case "stop":
            pane.send_keys("C-c")
            window.kill()
            notify.setTitle("Tmux app control").setMessage(f"{appName} stopped").flash()
        case "choose":
            trf = rofi('-theme+window+width', '25ch', '-theme+inputbar+children',
                       '[ prompt ]').setPrompt(appName).setTheme('overlays/center-dialog').makeDmenu()
            trf.addItem("Stop", 'no')
            trf.addItem("Restart", "refresh")
            select = trf.run()
            match select:
                case "Stop":
                    tmuxHelper('stop', command)
                case "Restart":
                    tmuxHelper('stop', command)
                    tmuxHelper('start', command)


def isProcRunning(procName):
    for item in psutil.process_iter(['name', 'cmdline']):
        if item.info['name'] == procName:
            return True
        try:
            if item.info["cmdline"][1].split('/')[-1] == procName:
                return True
        except (IndexError, TypeError):
            pass
    return False


def listAppImg():
    appPath = Path.home() / "programs"
    return [{"name": item.name, "cmd": [str(item.absolute())], "icon": "app"}
            for item in appPath.iterdir() if item.name.endswith('.AppImage')]


def listAvds():
    avds = sp.check_output(["emulator", "-list-avds",]).decode().strip().splitlines()
    return [{"name": avd, "icon": "smartphone",
             "cmd": ["emulator", f"@{avd}", "-feature", "-Vulkan", "-id", avd, "-restart-when-stalled"]} for avd in avds]


def idleTimerControl(action, icon):
    notify.setTitle("Auto-sleep").setMessage(f"{action}ing auto-sleep").setRofiImage(icon).flash()
    sp.Popen(["systemctl", "--user", action, "Idle.timer"])


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
            False: {"name": "XAutolock: OFF", "icon": "unprotected", "cmd": [f"{H}/.config/i3/scripts/i3lock.sh", "toggle"]}
        }[isProcRunning("xautolock")],
        {
            True:  {'name': "Auto sleep: ON", "icon": "auto-sleep-on", "cmd": [idleTimerControl, "stop", "green-tea"]},
            False: {'name': "Auto sleep: OFF", "icon": "green-tea", "cmd": [idleTimerControl, "start", "auto-sleep-on"]}
        }[sp.run(["systemctl", "--user", "is-active", "Idle.timer"]).returncode == 0],
        {"name": "Cinnamon settings", "icon": "gnome-settings",
         "cmd": ['cinnamon-settings']},
        {"name": "Theme settings", "icon": "cinnamon-preferences-color",
         "cmd": ['cinnamon-settings', 'themes']},
        {"name": SEP[0], 'icon': SEP[1]},
        {"name": "HF builds", "icon": "apk-64",
         "cmd": ['rofi-apkInstaller.sh', f'{H}/HF-data/builds']},
        {"name": "Restmail", "icon": "email",
         "cmd": ["restmail"]},
        *listAvds(),
        {"name": "AWS VPN", "icon": "VPN",
         "cmd": ["bash", "-c", r"""if ! i3-msg '[class="AWS VPN Client"]' focus; then
                        dex /usr/share/applications/awsvpnclient.desktop; fi """]},
        {
            True:  {"name": "Stop MITM", "icon": "hacker-activity", "cmd": [tmuxHelper, "stop", "mitmweb"]},
            False: {"name": "Start MITM", "icon": "hacker-activity", "cmd": [tmuxHelper, "start", "mitmweb"]}
        }[isProcRunning('mitmweb')],
        {
            True:  {"name": "Stop Appium", "icon": "appium", "cmd": [tmuxHelper, "stop", "appium"]},
            False: {"name": "Start Appium", "icon": "appium", "cmd": [tmuxHelper, "start", "appium"]}
        }[isProcRunning('appium')],
        {
            True:  {"name": "Stop UxPlay", "icon": "airplay", "cmd": [tmuxHelper, "choose", "uxplay -a -nc -reg -nohold -reset 1"]},
            False: {"name": "Start UxPlay", "icon": "airplay", "cmd": [tmuxHelper, "start", "uxplay -a -nc -reg -nohold -reset 1"]}
        }[isProcRunning('uxplay')],
        {"name": SEP[0], 'icon': SEP[1]},
        {"name": "Screen recorder", "icon": "recording",
         "cmd": ["dex", "/usr/share/applications/simplescreenrecorder.desktop"]},
        {"name": "Window inspector", "icon": "inspection",
         "cmd": ['bash', '-c', r'''output=$(xprop | grep "WM_NAME\|WM_CLASS\|ROLE\|WINDOW_TYPE")
            yad --text-info --title="Window Properties" \
            --window-icon=stock_search \
            --width=1000 --height=300 \
            --wrap --center --button=Close:1 --editable=false <<< "$output" ''']},
        {"name": "External monitor", "icon": 'display-settings',
         "cmd": ["monitorControl"]},
        *listAppImg()
    ]

    def makeRofi(self):
        rf.makeDmenu()
        for item in ControlCenter.CONTROLERS:
            rf.addItem(item['name'], item['icon'])

        selected = rf.run()
        if selected.startswith(W):
            confirm = rf.yesNo()
            if confirm == 'No':
                exit(0)
        return selected

    def find(self, name):
        for item in ControlCenter.CONTROLERS:
            if item['name'] == name:
                return item
        return {}

    def run(self, name):
        cmd = self.find(name).get('cmd')
        if not cmd:
            return
        if isinstance(cmd[0], types.FunctionType):
            cmd[0](*cmd[1:])
        else:
            sp.Popen(cmd)


def main():
    cc = ControlCenter()
    select = cc.makeRofi()
    cc.run(select)
