import subprocess as sp
import json
from rockytools import rofi

EJECT_ALL = "Eject all"
MOUNT_ALL = "Mount all"
REFRESH_MMC = "Refresh MMC slot"
NO_DRIVE = "No external drive "


def flash(title, msg):
    sp.Popen(["notify-send", "-t", "3000", "-ea", "Ext Disk Manager", title, msg])


class Block:
    def __init__(self, data):
        self.data = data

    @property
    def model(self):
        return self.data.get("model", "")

    @property
    def label(self):
        return self.data.get("label", "")

    @property
    def uuid(self):
        return self.data.get("uuid", "")

    @property
    def size(self):
        return self.data.get("size", "")

    @property
    def mount(self):
        return self.data.get("mountpoint", "")

    @property
    def icon(self):
        if self.tran == "usb":
            return "usb-flash-drive"
        if self.tran == "mmc":
            return "memory-card"
        return "disk"

    @property
    def listname(self):
        prefix = 'Eject' if self.mount else 'Mount'
        entry = []
        for k in [self.model, self.label, self.uuid, self.size]:
            if k:
                entry.append(k)
        return f"{prefix} > " + " | ".join(entry)

    @property
    def rofiItem(self):
        return self.listname, self.icon

    @property
    def tran(self):
        return self.data["tran"]

    @property
    def path(self):
        return self.data['path']


class BlockManager:
    def __init__(self):
        output = sp.check_output(["lsblk", "-JO"]).decode("utf-8")
        self.rofi = rofi("-theme", "overlays/center-dialog", '-p', 'Drive manager')
        self.data = json.loads(output)["blockdevices"]
        self.blocks = []
        for block in self.data:
            model = block["model"]
            tran = block["tran"]
            children = block.get("children", [])
            hotplug = block['hotplug']
            if not hotplug:
                continue
            if not children:
                toAdd = block
            else:
                for child in children:
                    hotplug = child['hotplug']
                    if not hotplug:
                        continue
                    child["model"] = model
                    child["tran"] = tran
                    toAdd = child

            self.blocks.append(Block(toAdd))

    def getMountedBlocks(self):
        blocks = []
        for block in self.blocks:
            if block.mount:
                blocks.append(block)
        return blocks

    def getUnmountedBlock(self):
        blocks = []
        for block in self.blocks:
            if not block.mount:
                blocks.append(block)
        return blocks

    def rofiListBlock(self):
        self.rofi.makeDmenu()
        maxWidth = len(NO_DRIVE)
        for block in self.getMountedBlocks() + self.getUnmountedBlock():
            self.rofi.addItem(*block.rofiItem)
            if len(block.listname) > maxWidth:
                maxWidth = len(block.listname)
        if self.rofi.isMenuEmpty():
            self.rofi.addItem(NO_DRIVE, "shrug")
        self.rofi.addItem('-' * maxWidth, "zigzag")
        self.rofi.addItem(REFRESH_MMC, 'loading-arrow')
        if self.countUnmounted():
            self.rofi.addItem(MOUNT_ALL, "external-hard-drive")
        if self.countMounted():
            self.rofi.addItem(EJECT_ALL, "eject-red")
        return self.rofi.run(addArgs=['-theme+window+width', f'{maxWidth+10}ch'])

    def findBlock(self, name):
        for block in self.blocks:
            if name == block.listname:
                return block

    def count(self):
        return len(self.blocks)

    def countUnmounted(self):
        return len(self.getUnmountedBlock())

    def countMounted(self):
        return len(self.getMountedBlocks())

    def mountBlock(self, block):
        result = sp.run(["udisksctl", "mount", "-b", block.path], capture_output=True, text=True)
        if result.stdout:
            flash("Disk change", result.stdout)
        else:
            flash("Disk change", result.stdout)

        return self

    def unmountBlock(self, block):
        result = sp.run(["udisksctl", "unmount", "-b", block.path], capture_output=True, text=True)
        if result.stdout:
            flash("Disk change", result.stdout)
        else:
            flash("Disk change", result.stdout)


def main():
    bm = BlockManager()
    selected = bm.rofiListBlock()
    if selected == EJECT_ALL:
        for block in bm.blocks:
            if block.mount:
                bm.unmountBlock(block)
        return

    if selected == MOUNT_ALL:
        for block in bm.blocks:
            if not block.mount:
                bm.mountBlock(block)
        return

    if selected == REFRESH_MMC:
        sp.call(['sudo', 'modprobe', '-r', 'rtsx_pci_sdmmc'])
        sp.call(['sudo', 'modprobe', 'rtsx_pci_sdmmc'])
        return

    block = bm.findBlock(selected)
    if not block:
        return
    if block.mount:
        bm.unmountBlock(block)
    else:
        bm.mountBlock(block)
