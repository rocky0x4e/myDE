import subprocess as sp
import json
from lib.fuzzel import fuzzel

DEFAULT_ROW_ICON = 'notification'


def main():
    rawHistory = sp.check_output(["makoctl", "history", "-j"]).decode()
    history = json.loads(rawHistory)
    fz = fuzzel().makeTable().setPrompt("Mako history ").setAnchor("bottom").setWindowWidth("150ch")
    for item in history:
        summary = item['summary']
        body = str(item['body']).splitlines()
        body = '|'.join(body)
        if not (summary or body):
            continue
        appname = item['app_name']
        id = item["id"]
        icon = item['app_icon'] or DEFAULT_ROW_ICON
        fz.addTableRow(row=[id, appname, summary, body], icon=icon)
    fz.fmtTable(" | ")
    fz.addItem("Reload config", "refresh")
    if fz.isMenuEmpty():
        fz.setMesg("No history").hidePrompt()
    else:
        fz.addItem("Clear history", 'delete')
    fz.addItem("Generate test history", 'zip-line')
    select = fz.run()
    if select == "Clear history":
        sp.run(['pkill', 'mako'])
    elif select == "Reload config":
        sp.run(['makoctl', 'reload'])
    elif select == "Generate test history":
        from lib.notification import NotifySend
        d = NotifySend().setTimeout(10000)
        d.setTitle("test 1 title").setMessage("test 1 message, not transient, no appname").flash()
        d.setAppName("test app").setTitle("test 2 low urgency")\
            .setMessage("test 2 message, not transient")\
            .setUrgencyLow().flash()
        d.setAppName("test app").setTitle("test 2 critical urgency")\
            .setMessage("test 2 message, not transient")\
            .setUrgencyCrit().flash()
        d.setAppName("test app").setTitle("test 2 normal urgency")\
            .setMessage("test 2 message, not transient")\
            .setUrgencyNormal().flash()
        d.setAppName("test app").setTitle("test 2 normal urgency")\
            .setMessage("Lorem Ipsum is simply dummy text of the printing and typesetting industry."
                        "Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,"
                        "when an unknown printer took a galley of type and scrambled it to make a type specimen book."
                        "It has survived not only five centuries, "
                        "but also the leap into electronic typesetting, remaining essentially unchanged. "
                        "It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, "
                        "and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.")\
            .setUrgencyNormal().flash()
        d.setAppName("test app").setTitle("test 3 title").setMessage("test 3 message, transient").setTransient().flash()
