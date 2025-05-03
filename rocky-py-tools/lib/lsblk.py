import subprocess as sp
import json


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
    def tran(self):
        return self.data["tran"]

    @property
    def path(self):
        return self.data['path']


class StorageBlockCtl:
    def __init__(self):
        self.blocks = []
        self.listBlocks()

    def listBlocks(self):
        output = sp.check_output(["lsblk", "-JO"]).decode("utf-8")
        data = json.loads(output)["blockdevices"]
        self.blocks = []
        for block in data:
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
        return self

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
        return sp.run(["udisksctl", "mount", "-b", block.path], capture_output=True, text=True)

    def unmountBlock(self, block):
        return sp.run(["udisksctl", "unmount", "-b", block.path], capture_output=True, text=True)
