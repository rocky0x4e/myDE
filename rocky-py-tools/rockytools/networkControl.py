import subprocess as sp
from lib.rofi import rofi
from lib.network import NetworkCtl, ResolveCtl
from lib.notification import DefautNotifier

ICONS = {
    '802-11-wireless': {True: "wifi", False: "wifi-no"},
    'loopback': {True: "loop-arrow", False: "loop-arrow"},
    'bridge': {True: "bridge", False: "bridge"},
    'tun': {True: "tunnel", False: "tunnel"}
}
SHOW_MORE = "Show more"
SHOW_LESS = "Show less"
NET_MAN = "Open Network Manager"
TOGGLE = {True: "down", False: "up"}
notify = DefautNotifier().setAppName("Network manager").setTransient()
netMan = NetworkCtl()


def showMenu(context, menuType):
    if menuType == SHOW_LESS:
        rf = rofi().makeDmenu().setTheme('overlays/thin-side-bar').setPrompt("Network")
        rf.addItem(NET_MAN, "manager")
        rf.addItem(f"Private DNS: {context['status']}", context['icon'])
        rf.addItem(SHOW_MORE, "down-chevron")
        rf.addItem(*rofi.separator(30, "Connections"))
        for con in netMan.connections:
            if "802" in con['type']:
                rf.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
        return rf.run()
    if menuType == SHOW_MORE:
        rfAll = rofi().makeDmenu().setTheme('overlays/thin-side-bar').setPrompt("Network")
        rfAll.addItem(NET_MAN, "manager")
        rfAll.addItem(f"Private DNS: {context['status']}", context['icon'])
        rfAll.addItem(SHOW_LESS, "up-chevron")
        rfAll.addItem(*rofi.separator(30, "Connections"))
        for con in netMan.connections:
            rfAll.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
        return rfAll.run()
    return ""


def main():
    resolveCtl = ResolveCtl()
    isPrivateDns = resolveCtl.isPrivateDns()
    dnsSettings = {"isPrivateDns": isPrivateDns,
                   "status": {True: "On", False: "OFF"}[isPrivateDns],
                   "icon": {True: "secure", False: "unprotected"}[isPrivateDns]}

    select = showMenu(dnsSettings, SHOW_LESS)
    while select in (SHOW_LESS, SHOW_MORE):
        select = showMenu(dnsSettings, select)

    if select == NET_MAN:
        sp.Popen(["cinnamon-settings", "network"])
        return
    if "Private DNS: " in select:
        select = select.split(":")[0]
        r = resolveCtl.togglePrivateDNS()
        notify.setTitle("Private DNS settings").setMessage(f"{select}: {r}").flash()
        return
    if netMan.find_connections(select):
        r = netMan.toggleConnection(select)
        notify.setTitle("Connection status").setMessage(r).flash()
