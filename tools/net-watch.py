#!/usr/bin/env python3

import subprocess
import re
from pathlib import Path
import requests
import socket
import json
import logging
from logging.handlers import RotatingFileHandler


# === CONFIGURATION ===
INTERFACES = ["wlp1s0", "eno1", "wlp0s20f3"]  # Or auto-detect

class DataFile:
    DATA_PATH = Path.home() / ".net-watch"
    def __init__(self, filename):
        self.file = DataFile.DATA_PATH / filename
        self.data = {}

    def touch (self):
        self.file.touch(exist_ok=True)
        return self

    def loadData(self):
        data = self.file.read_text().strip()
        self.data = {} if not data else json.loads(data)
        return self

    def checkMac(self, mac):
        return mac in self.data

    def addData(self, data):
        self.data.update(data)
        return self

    def write(self):
        with open(str(self.file.absolute()), "w+") as f:
            json.dump(self.data,f , indent=3)
        return self

    def isEmpty(self):
        return True if not self.data else False

# KNOWN_FILE = DataFile("known_devices.json").touch().loadData()
LOG_FILE = DataFile("network_new_devices.log").touch()
WHITELIST_FILE = DataFile("network_whitelist.json").touch().loadData()
BLOCKLIST_FILE = DataFile("network_blocklist.json").touch().loadData()
NTFY_TOPIC = "rocky-lan-alerts"

logger = logging.getLogger("network-watch")
logger.setLevel(logging.INFO)
# Rotate after 1MB, keep 3 old logs
handler = RotatingFileHandler(str(LOG_FILE.file.absolute()), maxBytes=500_000, backupCount=3)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "[%Y-%m-%d %H:%M:%S]")
handler.setFormatter(formatter)

logger.addHandler(handler)

def run_arp_scan(interface):
    try:
        output = subprocess.check_output(
            ["arp-scan", "--interface", interface, "--localnet"],
            stderr=subprocess.DEVNULL
        ).decode()
        return output
    except subprocess.CalledProcessError as e:
        return ""

def extract_devices(scan_output):
    device_regex = re.compile(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]{17})\s+(.+)")
    return device_regex.findall(scan_output)

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "unknown-host"

def notify(ip, mac, vendor, hostname, iface):
    msg = (f"📡 New device detected on {iface}\n"
            f"IP: {ip}\n"
            f"MAC: {mac}\n"
            f"Vendor: {vendor}\n"
            f"Host: {hostname}")
    try:
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=msg.encode("utf-8"))
    except Exception as e:
        pass  # Optionally log this error

def scan_interface(interface):
    output = run_arp_scan(interface)
    devices = extract_devices(output)

    for ip, mac, vendor in devices:
        mac = mac.lower()
        if BLOCKLIST_FILE.checkMac(mac):
            continue
        vendor = vendor.strip()
        hostname = get_hostname(ip)
        data = {mac:{"ip":ip, "vendor":vendor, "hostname":hostname}}


        # if not KNOWN_FILE.checkMac(mac):
        #     hostname = get_hostname(ip)
        #     KNOWN_FILE.addData(data)

        if WHITELIST_FILE.isEmpty() or WHITELIST_FILE.checkMac(mac):
            notify(ip, mac, vendor, hostname, interface)

        logger.info(f"New device @ {interface}: {data}")

    # KNOWN_FILE.write()

def main():
    for iface in INTERFACES:
        scan_interface(iface)

if __name__ == "__main__":
    main()
