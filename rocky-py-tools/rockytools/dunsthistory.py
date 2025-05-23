import subprocess as sp
import json
from lib.rofi import rofi


def main():
    rawHistory = sp.check_output(["dunstctl", "history"]).decode()
    history = json.loads(rawHistory)['data'].pop()
    rf = rofi({'-theme+listview+columns': '1'}).makeTable(4).setPrompt("Dunst history")
    for item in history:
        summary = item['summary']['data'].strip()
        body = item['body']['data'].strip()
        if not (summary or body):
            continue
        # message = item['message']['data'].strip()
        appname = item['appname']['data'].strip()
        id = item["id"]["data"]
        icon = item['icon_path']['data']
        rf.addTableItem(id, column=0)
        rf.addTableItem(appname, column=1)
        rf.addTableItem(summary, column=2)
        rf.addTableItem(body, column=3)
        rf.addPseudoTableIcon(icon)
    rf.fmtPseudoTable()
    rf.addItem("Clear history", 'delete') if not rf.isMenuEmpty() else rf.addMesg("No history")
    select = rf.run()
    if select == "Clear history":
        sp.run(['dunstctl', 'history-clear'])


main()
