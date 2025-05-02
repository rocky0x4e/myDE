from gi.repository import Gtk, GtkSource, Gdk
import gi
import sys
import os
import subprocess as sp
from pathlib import Path
from rockytools import rofi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")

NOTE_PATH = Path.home() / "Notes"


class Notepad(Gtk.Window):
    def __init__(self, filename=None):
        super().__init__(title=filename.split("/")[-1])
        self.set_wmclass("Rofi-note", "Rofi-note")
        self.set_default_size(800, 600)
        self.set_border_width(6)

        self.filename = filename

        # Apply dark theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", True)

        # Text buffer and view
        lm = GtkSource.LanguageManager()
        self.buffer = GtkSource.Buffer()
        self.buffer.set_language(lm.get_language("bash"))

        self.view = GtkSource.View.new_with_buffer(self.buffer)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view.set_show_line_numbers(True)
        self.view.set_monospace(True)

        if filename and os.path.exists(filename):
            with open(filename, "r") as f:
                self.buffer.set_text(f.read())

        # Scrolled window
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(self.view)

        # Buttons
        save_btn = Gtk.Button(label="💾 Save")
        save_btn.connect("clicked", self.save_file)

        cancel_btn = Gtk.Button(label="❌ Cancel")
        cancel_btn.connect("clicked", self.cancel)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_box.pack_start(save_btn, False, False, 0)
        btn_box.pack_start(cancel_btn, False, False, 0)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.pack_start(scroll, True, True, 0)
        vbox.pack_start(btn_box, False, False, 0)

        self.add(vbox)
        self.connect("destroy", Gtk.main_quit)
        self.connect("key-press-event", self.on_key_press)

    def save_file(self, _widget=None):
        if self.filename:
            start, end = self.buffer.get_bounds()
            text = self.buffer.get_text(start, end, True)
            with open(self.filename, "w") as f:
                f.write(text)
            print("Saved:", self.filename)
        Gtk.main_quit()

    def cancel(self, _widget=None):
        print("Edit cancelled.")
        Gtk.main_quit()

    def save_as(self):
        dialog = Gtk.FileChooserDialog(
            title="Save As",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )
        dialog.set_do_overwrite_confirmation(True)

        if dialog.run() == Gtk.ResponseType.OK:
            self.filename = dialog.get_filename()
            self.save_file()
        dialog.destroy()

    def delete_file(self):
        if not self.filename:
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Delete file?",
        )
        dialog.format_secondary_text(self.filename)
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            try:
                os.remove(self.filename)
            except FileNotFoundError:
                pass
            print("File deleted:", self.filename)
            Gtk.main_quit()

    def on_key_press(self, widget, event):
        keyval = event.keyval
        state = event.state

        ctrl = state & Gdk.ModifierType.CONTROL_MASK
        shift = state & Gdk.ModifierType.SHIFT_MASK

        if keyval == Gdk.KEY_Escape:
            self.save_file()
        elif ctrl and shift and keyval == Gdk.KEY_S:
            self.save_as()
        elif ctrl and keyval == Gdk.KEY_Delete:
            self.delete_file()


def rofiSelectNote():
    rf = rofi('-theme', 'overlays/center-dialog')
    for item in NOTE_PATH.iterdir():
        rf.addItem(item.name, "note")
    return rf.run()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        path = rofiSelectNote()

    if not Path(path).exists():
        path = str(NOTE_PATH / path)
    win = Notepad(filename=path)
    win.show_all()
    Gtk.main()
