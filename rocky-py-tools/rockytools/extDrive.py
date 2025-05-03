import subprocess as sp
from lib.rofi import rofi
from lib.notifysend import NotifySend
from lib.lsblk import StorageBlockCtl

EJECT_ALL = "Eject all"
MOUNT_ALL = "Mount all"
REFRESH_MMC = "Refresh MMC slot"
NO_DRIVE = "No external drive "

notify = NotifySend().setAppName("Ext Disk Manager").setTimeout(3000).setTransient()


def mountBlock(self, block):
    result = sp.run(["udisksctl", "mount", "-b", block.path], capture_output=True, text=True)
    if result.stdout:
        notify.setTitle('Disk change').setMessage(result.stdout).flash()
    else:
        notify.setTitle('Disk change').setMessage(result.stderr).flash()
    return self


def unmountBlock(self, block):
    result = sp.run(["udisksctl", "unmount", "-b", block.path], capture_output=True, text=True)
    if result.stdout:
        notify.setTitle('Disk change').setMessage(result.stdout).flash()
    else:
        notify.setTitle('Disk change').setMessage(result.stderr).flash()


def main():
    bm = StorageBlockCtl()
    rf = rofi("-theme", "overlays/center-dialog", '-p', 'Drive manager').makeDmenu()
    maxWidth = len(NO_DRIVE)
    for block in bm.getMountedBlocks() + bm.getUnmountedBlock():
        rf.addItem(block.listname, block.icon)
        if len(block.listname) > maxWidth:
            maxWidth = len(block.listname)
    if rf.isMenuEmpty():
        rf.addItem(NO_DRIVE, "shrug")
    rf.addItem('-' * maxWidth, "zigzag")
    rf.addItem(REFRESH_MMC, 'loading-arrow')
    if bm.countUnmounted():
        rf.addItem(MOUNT_ALL, "external-hard-drive")
    if bm.countMounted():
        rf.addItem(EJECT_ALL, "eject-red")

    selected = rf.run(addArgs=['-theme+window+width', f'{maxWidth+10}ch'])
    if selected == EJECT_ALL:
        for block in bm.blocks:
            if block.mount:
                r = bm.unmountBlock(block)
                msg = r.stdout if r.stdout else r.stderr
                notify.setTitle('Disk change').setMessage(msg).flash()
        return

    if selected == MOUNT_ALL:
        for block in bm.blocks:
            if not block.mount:
                r = bm.mountBlock(block)
                msg = r.stdout if r.stdout else r.stderr
                notify.setTitle('Disk change').setMessage(msg).flash()
        return

    if selected == REFRESH_MMC:
        sp.call(['sudo', 'modprobe', '-r', 'rtsx_pci_sdmmc'])
        sp.call(['sudo', 'modprobe', 'rtsx_pci_sdmmc'])
        return

    block = bm.findBlock(selected)
    if not block:
        return
    if block.mount:
        r = bm.unmountBlock(block)
        msg = r.stdout if r.stdout else r.stderr
        notify.setTitle('Disk change').setMessage(msg).flash()
    else:
        r = bm.mountBlock(block)
        msg = r.stdout if r.stdout else r.stderr
        notify.setTitle('Disk change').setMessage(msg).flash()
