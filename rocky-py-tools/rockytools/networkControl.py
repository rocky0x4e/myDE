import subprocess as sp
from lib.rofi import rofi
from lib.network import NetworkCtl, ResolveCtl
from lib.notifysend import NotifySend

ICONS = {
    '802-11-wireless': {True: "wifi", False: "wifi-no"},
    'loopback': {True: "loop-arrow", False: "loop-arrow"},
    'bridge': {True: "bridge", False: "bridge"},
    'tun': {True: "tunnel", False: "tunnel"}
}
SHOW_ALL = "Show more"
NET_MAN = "Open Network Manager"
TOGGLE = {True: "down", False: "up"}
notify = NotifySend().setAppName("Network manager").setTransient()


def main():
    netMan = NetworkCtl()
    resolveCtl = ResolveCtl()
    resolveCtlManagedInt = resolveCtl.getManagedInterfaces()
    rf = rofi().makeDmenu().setTheme('overlays/thin-side-bar').setPrompt("Network")
    rfAll = rofi().makeDmenu().setTheme('overlays/thin-side-bar').setPrompt("Network")
    rf.addItem(NET_MAN, "manager")
    rf.addItem(SHOW_ALL, "ethernet")
    rf.addItem(*rofi.separator(30, "Private DNS settings"))
    rfAll.addItem(NET_MAN, "manager")
    rfAll.addItem(*rofi.separator(30, "Private DNS settings"))
    for i in resolveCtlManagedInt:
        icon = "secure" if resolveCtl.isPrivateDns(i) else "unprotected"
        rf.addItem(i, icon)
        rfAll.addItem(i, icon)

    rf.addItem(*rofi.separator(30, "Connections"))
    rfAll.addItem(*rofi.separator(30, "Connections"))

    select = ''
    for con in netMan.connections:
        if "802" in con['type']:
            rf.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
        rfAll.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
    select = rf.run()
    if select == SHOW_ALL:
        select = rfAll.run()
    if select == NET_MAN:
        sp.Popen(["cinnamon-settings", "network"])
        return
    if select in resolveCtlManagedInt:
        r = resolveCtl.togglePrivateDNS(select)
        notify.setTitle("Private DNS settings").setMessage(f"{select} : {r}").flash()
        return
    r = netMan.toggleConnection(select)
    notify.setTitle("Connection status").setMessage(r).flash()
