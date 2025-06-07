import i3ipc
from lib.rofi import rofi

i3 = i3ipc.Connection()
rf = rofi().makeTable(2).setTheme("overlays/center-dialog").setPrompt("I3 scratchpad")

for leaf in i3.get_tree().scratchpad().leaves():
    rf.addTableItem(leaf.ipc_data['id'], column=0)
    rf.addTableItem(leaf.ipc_data['window_properties']['title'], column=1)

rf.fmtPseudoTable()
select = rf.run()
windowId = int(select.split(" | ")[0])
i3.get_tree().find_by_id(windowId).command('focus')
