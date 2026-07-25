import subprocess as sp
from lib.network import NetworkCtl, ResolveCtl
from lib.fuzzel import fuzzel
from lib.notification import DefautNotifier

ICONS = {
    '802-11-wireless': {"activated": "wifi", "no": "wifi-no"},
    'loopback': {"activated": "loop-arrow", "no": "loop-arrow"},
    'bridge': {"activated": "bridge", "no": "bridge"},
    'tun': {"activated": "tunnel", "no": "tunnel"}
}
for k, v in ICONS.items():
    ICONS[k]["activating"] = "loading-arrow"


class MenuItem:
    SHOW_MORE = "Show more"
    SHOW_LESS = "Show less"
    NET_MAN = "Open Network Manager"


TOGGLE = {True: "down", False: "up"}
notify = DefautNotifier().setAppName("Network manager").setTransient()
netMan = NetworkCtl()


def showMenu(context, menuType):
    if menuType == MenuItem.SHOW_LESS:
        fz = fuzzel().makeDmenu().setPrompt("Network").setAnchor("top-right")
        fz.addItem(MenuItem.NET_MAN, "manager")
        fz.addItem(f"Private DNS: {context['status']}", context['icon'])
        fz.addItem(MenuItem.SHOW_MORE, "down-chevron")
        fz.addItem(*fuzzel.separator(30, "Connections"))
        for con in netMan.connections:
            if "802" in con.type:
                fz.addItem(con.name + " connecting..." if con.state ==
                           "activating" else con.name, ICONS[con.type][con.state])
        return fz.run()
    if menuType == MenuItem.SHOW_MORE:
        fzAll = fuzzel().makeDmenu().setPrompt("Network").setAnchor("right")
        fzAll.addItem(MenuItem.NET_MAN, "manager")
        fzAll.addItem(f"Private DNS: {context['status']}", context['icon'])
        fzAll.addItem(MenuItem.SHOW_LESS, "up-chevron")
        fzAll.addItem(*fuzzel.separator(30, "Connections"))
        for con in netMan.connections:
            fzAll.addItem(con.name + " connecting..." if con.state ==
                          "activating" else con.name, ICONS[con.type][con.state])
        return fzAll.run()
    return ""


def main():
    resolveCtl = ResolveCtl()
    isPrivateDns = resolveCtl.isPrivateDns()
    dnsSettings = {"isPrivateDns": isPrivateDns,
                   "status": {True: "On", False: "OFF"}[isPrivateDns],
                   "icon": {True: "secure", False: "unprotected"}[isPrivateDns]}

    select = showMenu(dnsSettings, MenuItem.SHOW_LESS)
    while select in (MenuItem.SHOW_LESS, MenuItem.SHOW_MORE):
        select = showMenu(dnsSettings, select)

    if select == MenuItem.NET_MAN:
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
