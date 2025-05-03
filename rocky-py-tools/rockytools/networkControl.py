import subprocess as sp
from lib.rofi import rofi
from lib.networkctl import NetworkCtl
from lib.notifysend import NotifySend

ICONS = {
    '802-11-wireless': {True: "wifi", False: "wifi-no"},
    'loopback': {True: "loop-arrow", False: "loop-arrow"},
    'bridge': {True: "bridge", False: "bridge"}
}
SHOW_ALL = "Show more"
NET_MAN = "Open Network Manager"
DNS_SEC = "Private DNS setting"
TOGGLE = {True: "down", False: "up"}


def main():
    netMan = NetworkCtl()
    rf = rofi('-theme', 'overlays/thin-side-bar', '-p', 'Network').makeDmenu()
    rfAll = rofi('-theme', 'overlays/thin-side-bar', '-p', 'Network').makeDmenu()

    select = ''
    for con in netMan.connections:
        if con['type'] != 'loopback' and con['type'] != 'bridge':
            rf.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
        rfAll.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
    rf.addItem(DNS_SEC, "dns")
    rf.addItem(NET_MAN, "manager")
    rf.addItem(SHOW_ALL, "ethernet")
    rfAll.addItem(DNS_SEC, "dns")
    rfAll.addItem(NET_MAN, "manager")
    select = rf.run()
    if select == SHOW_ALL:
        select = rfAll.run()
    if select == NET_MAN:
        sp.Popen(["cinnamon-settings", "network"])
        exit(0)
    if select == DNS_SEC:
        sp.Popen(["rofi-dnssec.sh"])
        exit(0)

    r = netMan.toggleConnection(select)
    NotifySend().setAppName("Network manager")\
        .setTransient()\
        .setTitle(select)\
        .setMessage(r)\
        .flash()
