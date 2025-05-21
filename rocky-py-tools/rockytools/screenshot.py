from datetime import datetime
import time
from gi.repository import Gtk, GdkPixbuf, Gdk
import gi
import subprocess as sp
from pathlib import Path
from lib.notifysend import NotifySend
gi.require_version("Gtk", "3.0")

# Sample entries similar to "${entries[@]}" in your bash script
MODE_AREA = {"text": "Area", "icon": "edit-select-all"}
MODE_WINDOW = {"text": "Window", "icon": "window_fullscreen"}
MODE_WHOLE = {"text": "Whole screen", "icon": "cs-screen"}
ENTRIES = (MODE_AREA, MODE_WINDOW, MODE_WHOLE)
SAVE_FILE = "Save to file (Ctrl+Enter)"
SAVE_CLIP = "Save to clipboard (Enter)"

SETTINGS = {'saveMode': "", 'grabMode': "", "delay": 0}
APP_NAME = "R.Screenshot"

NOTIFY = NotifySend().setAppName(APP_NAME).setTransient().setTimeout(3000).setTitle("Screenshot taken")


def do_screenshot():
    if not SETTINGS["saveMode"]:
        return
    notifyMsg = "Saved to: "
    cmd = ['maim']
    if SETTINGS['grabMode'] == MODE_WINDOW["text"]:
        wid = sp.check_output(["xdotool", "selectwindow"]).decode().strip()
        cmd.extend(['-i', wid])
    if SETTINGS['grabMode'] == MODE_AREA["text"]:
        cmd.append("-s")
    if SETTINGS["grabMode"] == MODE_WHOLE["text"]:
        time.sleep(0.3)

    if SETTINGS['saveMode'] == SAVE_FILE:
        now = datetime.now()
        folder = Path.home() / "Pictures" / "screenshots"
        file = folder / f"{now.strftime("%Y%m%d-%H%M%S")}.png"
        notifyMsg += str(folder.absolute())
        cmd.append(str(file.absolute()))

    time.sleep(SETTINGS["delay"]) if SETTINGS['delay'] else 0
    maimRun = sp.Popen(cmd, stderr=sp.PIPE, stdout=sp.PIPE)
    if SETTINGS["saveMode"] == SAVE_CLIP:
        notifyMsg += "Clipboard"
        sp.call(["xclip", "-selection", "clipboard", "-t", "image/png"], stdin=maimRun.stdout)
    else:
        maimRun.communicate()
    NOTIFY.setMessage(notifyMsg).flash()


class ScreenGrabber(Gtk.Window):
    def __init__(self):

        # Create the main window
        super().__init__(title=APP_NAME)
        self.set_default_size(0, 0)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self.onKeyPressed)
        self.set_icon_name("camera-photo")

        # Create a list store (icon, description)
        self.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)
        for item in ENTRIES:
            pixbuf = Gtk.IconTheme.get_default().load_icon(item['icon'], 32, 0)
            self.store.append([pixbuf, item["text"]])

        # Create tree view
        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.set_headers_visible(False)

        # Icon column
        renderer_pixbuf = Gtk.CellRendererPixbuf()
        column_icon = Gtk.TreeViewColumn("", renderer_pixbuf, pixbuf=0)
        self.treeview.append_column(column_icon)

        # Text column
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("", renderer_text, text=1)
        self.treeview.append_column(column_text)

        # Horizontal box for label + spin button
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Label
        label = Gtk.Label(label="Delay (s):")
        hbox.pack_start(label, False, False, 0)

        # SpinButton with adjustment
        adjustment = Gtk.Adjustment(value=1, lower=0, upper=100, step_increment=1, page_increment=10, page_size=0)
        self.spin = Gtk.SpinButton()
        self.spin.set_adjustment(adjustment)
        self.spin.set_value(0)
        self.spin.set_digits(0)
        self.spin.set_numeric(True)
        self.spin.set_size_request(60, -1)  # compact width
        hbox.pack_end(self.spin, False, False, 0)

        # Button box
        button_box = Gtk.Box(spacing=6)
        button_box.set_halign(Gtk.Align.CENTER)

        def add_button(label, icon_name):
            image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            button = Gtk.Button()
            box = Gtk.Box(spacing=6)
            box.pack_start(image, False, False, 0)
            box.pack_start(Gtk.Label(label=label), False, False, 0)
            button.add(box)
            button.connect("clicked", self.onBtnClick)
            button_box.pack_start(button, False, False, 0)
            return button

        self.btnSaveClip = add_button(SAVE_CLIP, "clipit")
        self.btnSaveFile = add_button(SAVE_FILE, "emblem-photos")

        # Layout all in a VBox
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_border_width(10)

        vbox.pack_start(self.treeview, True, True, 0)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(button_box, False, False, 0)

        self.add(vbox)

    def getGrabOptions(self):
        selection = self.treeview.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            value = model[treeiter][1]

        return value, self.spin.get_value_as_int()

    # Action handlers

    def onKeyPressed(self, widget, event):
        keyval = event.keyval
        state = event.state
        ctrl = state & Gdk.ModifierType.CONTROL_MASK
        if ctrl:
            if keyval == Gdk.KEY_Return:
                self.btnSaveFile.emit("clicked")
        else:
            if keyval == Gdk.KEY_Escape:
                Gtk.main_quit()
            if keyval == Gdk.KEY_Return:
                self.btnSaveClip.emit('clicked')

    def onBtnClick(self, widget):
        SETTINGS['saveMode'] = widget.get_child().get_children()[1].get_label()
        SETTINGS['grabMode'], SETTINGS['delay'] = self.getGrabOptions()
        self.destroy()


def main():
    win = ScreenGrabber()
    win.show_all()
    Gtk.main()
    do_screenshot()
