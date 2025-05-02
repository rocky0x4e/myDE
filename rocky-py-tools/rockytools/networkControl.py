import subprocess as sp
from rockytools import rofi

ICONS = {
    '802-11-wireless': {True: "wifi", False: "wifi-no"},
    'loopback': {True: "loop-arrow", False: "loop-arrow"},
    'bridge': {True: "bridge", False: "bridge"}
}
SHOW_ALL = "Show more"
NET_MAN = "Open Network Manager"
DNS_SEC = "Private DNS setting"
TOGGLE = {True: "down", False: "up"}


class NetworkMan:
    def __init__(self):
        self.connections = []
        self.get_connecttions()
        self.rofi = rofi('-theme', 'overlays/thin-side-bar', '-p', 'Network')
        self.rofiAll = rofi('-theme', 'overlays/thin-side-bar', '-p', 'Network')

    def get_connecttions(self):
        data_all = sp.check_output(["nmcli", "-c", "no", "-t", "connection", "show"]).decode().strip()

        for line in data_all.splitlines():
            name, uuid, _type, device = line.split(":")
            self.connections.append({"uuid": uuid, "name": name, "type": _type, "dev": device})

    def find_connections(self, name):
        r = []
        for con in self.connections:
            if con["name"] == name:
                r.append(con)
        return r

    def rofiShowConnections(self):
        select = ''
        for con in self.connections:
            if con['type'] != 'loopback' and con['type'] != 'bridge':
                self.rofi.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
            self.rofiAll.addItem(con['name'], ICONS[con['type']][con["dev"] != ""])
        self.rofi.addItem(DNS_SEC, "dns")
        self.rofi.addItem(NET_MAN, "manager")
        self.rofi.addItem(SHOW_ALL, "ethernet")
        self.rofiAll.addItem(DNS_SEC, "dns")
        self.rofiAll.addItem(NET_MAN, "manager")
        select = self.rofi.run()
        if select == SHOW_ALL:
            select = self.rofiAll.run()
        if select == NET_MAN:
            sp.Popen(["cinnamon-settings", "network"])
            exit(0)
        if select == DNS_SEC:
            sp.Popen(["rofi-dnssec.sh"])
            exit(0)
        return select

    def toggleConnection(self, name):
        cons = self.find_connections(name)
        if len(cons) == 1:
            sp.run(["nmcli", "connection", TOGGLE[cons[0]['dev'] != ""], cons[0]['uuid']])
        else:  # more than 1 connection with same name
            menu = []
            toggle = {}
            for con in cons:
                toggle[con['uuid']] = TOGGLE[con['dev'] != ""]
                self.rofi.addItem(f"{con['name']} | {con['uuid']}", ICONS[con['type']][con["dev"] != ""])
            select = self._rofi(menu)
            uuid = select.split("|")[1].strip()
            sp.run(["nmcli", "connection", toggle[uuid], uuid])


def main():
    netMan = NetworkMan()
    select = netMan.rofiShowConnections()
    netMan.toggleConnection(select)
