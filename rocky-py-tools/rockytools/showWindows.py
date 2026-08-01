from lib.fuzzel import fuzzel
from lib.niri import niriwm

NAME_REPLACE_LIST = {"org.telegram.desktop": "org.telegram.desktop",
                     "ONLYOFFICE": "org.onlyoffice.desktopeditors"}


def iconReplacer(appId):
    for match, replace in NAME_REPLACE_LIST.items():
        if match in appId:
            return replace
    return appId


def main():
    sep = '| '
    fz = fuzzel().makeTable().setIconTheme().setWindowWidth(120)
    windows = niriwm.getWindows().shortByWorkspaceId()
    workspaces = niriwm.getWorkspaces()
    for window in windows.windowList:
        appIcon = iconReplacer(window.appId)
        fz.addTableRow(row=[window.appIdSort,
                            workspaces.getWsById(window.workspaceId).name,
                            window.title, window.id],
                       icon=appIcon)
    fz.fmtTable(sep)
    select = fz.run()
    windowId = select.split(sep)[-1].strip()
    niriwm.focusWindow(windowId)
