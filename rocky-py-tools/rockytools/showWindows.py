from lib.fuzzel import fuzzel
from lib.niri import niriwm


def main():
    fz = fuzzel().makeTable().setIconTheme().setWindowWidth(120)
    windows = niriwm.getWindows()
    groupedWindows = windows.groupByWorkspaceId()
    for _, wl in groupedWindows.items():
        for window in wl:
            fz.addTableRow(row=[window.appIdSort, window.title, window.id], icon=window.appId)
    sep = ' | '
    fz.fmtTable(sep)
    select = fz.run()
    windowId = select.split(sep)[-1].strip()
    niriwm.focusWindow(windowId)
