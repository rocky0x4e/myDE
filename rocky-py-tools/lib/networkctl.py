import subprocess as sp

ICONS = {
    '802-11-wireless': {True: "wifi", False: "wifi-no"},
    'loopback': {True: "loop-arrow", False: "loop-arrow"},
    'bridge': {True: "bridge", False: "bridge"}
}
SHOW_ALL = "Show more"
NET_MAN = "Open Network Manager"
DNS_SEC = "Private DNS setting"
TOGGLE = {True: "down", False: "up"}


class NetworkCtl:
    def __init__(self):
        self.connections = []
        self.get_connecttions()

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

    def toggleConnection(self, name):
        cons = self.find_connections(name)
        if len(cons) == 1:
            return sp.check_output(["nmcli", "connection", TOGGLE[cons[0]['dev'] != ""], cons[0]['uuid']]).decode().strip()
        else:  # more than 1 connection with same name
            self.rofi.makeDmenu()
            toggle = {}
            for con in cons:
                toggle[con['uuid']] = TOGGLE[con['dev'] != ""]
                self.rofi.addItem(f"{con['name']} | {con['uuid']}", ICONS[con['type']][con["dev"] != ""])
            select = self.rofi.run()
            uuid = select.split("|")[1].strip()
            return sp.check_output(["nmcli", "connection", toggle[uuid], uuid]).decode().strip()
