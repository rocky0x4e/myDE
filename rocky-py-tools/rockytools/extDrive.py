import subprocess as sp
from lib.fuzzel import fuzzel
from lib.notification import DefautNotifier
from lib.lsblk import StorageBlockCtl


class MenuItem:
    EJECT_ALL = "Eject all"
    MOUNT_ALL = "Mount all"
    REFRESH_MMC = "Refresh MMC slot"
    NO_DRIVE = "No external drive "


notify = DefautNotifier().setAppName("Ext Disk Manager").setTimeout(3000).setTransient()


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
    fz = fuzzel().makeDmenu().setPrompt('Drive manager ').setOutputLines(10)
    maxWidth = len(MenuItem.NO_DRIVE)
    for block in bm.getMountedBlocks() + bm.getUnmountedBlock():
        fz.addItem(block.listname, block.icon)
        if len(block.listname) > maxWidth:
            maxWidth = len(block.listname)
    if fz.isMenuEmpty():
        fz.addItem(MenuItem.NO_DRIVE, "shrug")
    fz.addItem('-' * maxWidth, "zigzag")
    fz.addItem(MenuItem.REFRESH_MMC, 'loading-arrow')
    if bm.countUnmounted():
        fz.addItem(MenuItem.MOUNT_ALL, "external-hard-drive")
    if bm.countMounted():
        fz.addItem(MenuItem.EJECT_ALL, "eject-red")

    selected = fz.setWindowWidth(f'{maxWidth+10}ch').run()
    if selected == MenuItem.EJECT_ALL:
        for block in bm.blocks:
            if block.mount:
                r = bm.unmountBlock(block)
                msg = r.stdout if r.stdout else r.stderr
                notify.setTitle('Disk change').setMessage(msg).flash()
        return

    if selected == MenuItem.MOUNT_ALL:
        for block in bm.blocks:
            if not block.mount:
                r = bm.mountBlock(block)
                msg = r.stdout if r.stdout else r.stderr
                notify.setTitle('Disk change').setMessage(msg).flash()
        return

    if selected == MenuItem.REFRESH_MMC:
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
