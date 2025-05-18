from lib.rofi import rofi
from lib.randr import RandR


def main():
    randr = RandR()

    rf = rofi().makeDmenu().setTheme('overlays/thin-side-bar').setPrompt('Display settings')
    for disp in randr.displays:
        if disp.isConnected:
            icon = "screen-active" if disp.isActive else "screen-inactive"
            rf.addItem(disp.name, icon)
    rf.addItem("Arandr", "display-settings")
    select = rf.run()

    if select == "Arandr":
        randr.openArandR()
    else:
        display = randr.findDisplay(select)
        randr.toggleDisplay(display, '--rotate', 'left')
