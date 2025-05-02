#!/usr/bin/env python3

import subprocess as sp

I = "\\x00icon\\x1f"
ICONS={
    '802-11-wireless':{True:"wifi",False:"wifi-no"},
    'loopback':{True:"loop-arrow",False:"loop-arrow"},
    'bridge':{True:"bridge",False:"bridge"}
    }
SHOW_ALL = "Show more"
NET_MAN = "Open Network Manager"
DNS_SEC = "Private DNS setting"
TOGGLE = {True: "down", False: "up"}

class NetworkMan:
    def __init__(self):
        self.connections = []
        self.get_connecttions()

    def get_connecttions(self):
        data_all = sp.check_output(["nmcli", "-c", "no", "-t", "connection", "show"]).decode().strip()

        for line in data_all.splitlines():
            name, uuid, _type, device = line.split(":")
            self.connections.append({"uuid": uuid, "name": name, "type": _type, "dev": device})

    def find_connections(self, name):
        r =[]
        for con in self.connections:
            if con["name"] == name: r.append(con)
        return r

    def _rofi(self, menu):
        echo = sp.Popen(["echo", "-en", "\n".join(menu)], stdout=sp.PIPE, stderr=sp.PIPE)
        return sp.check_output(['rofi', '-dmenu', '-i', '-theme', 'overlays/thin-side-bar', '-icon-theme', 'rofi',
                                  '-p', 'Network'], stdin=echo.stdout).decode().strip()

    def rofiShowConnections(self):
        menu = []
        menuAll = []
        select=''
        for con in self.connections:
            if con['type'] != 'loopback' and con['type'] != 'bridge':
                menu.append(f"{con['name']}{I}{ICONS[con['type']][con["dev"] != ""]}")
            menuAll.append(f"{con['name']}{I}{ICONS[con['type']][con["dev"] != ""]}")
        menu.append(f"{DNS_SEC}{I}dns")
        menu.append(f"{NET_MAN}{I}manager")
        menu.append(f"{SHOW_ALL}{I}ethernet")
        menuAll.append(f"{DNS_SEC}{I}dns")
        menuAll.append(f"{NET_MAN}{I}manager")
        select = self._rofi(menu)
        if select==SHOW_ALL:
            select = self._rofi(menuAll)
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
            sp.run(["nmcli", "connection", TOGGLE[cons[0]['dev']!=""], cons[0]['uuid']])
        else: # more than 1 connection with same name
            menu = []
            toggle = {}
            for con in cons:
                toggle[con['uuid']] =  TOGGLE[con['dev']!=""]
                menu.append(f"{con['name']} | {con['uuid']}{I}{ICONS[con['type']][con["dev"] != ""]}")
            select = self._rofi(menu)
            uuid = select.split("|")[1].strip()
            sp.run(["nmcli", "connection", toggle[uuid], uuid])


netMan = NetworkMan()
select = netMan.rofiShowConnections()
netMan.toggleConnection(select)