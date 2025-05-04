from gi.repository import Gtk, GtkSource, Gdk, GLib
import gi
import sys
import os
from pathlib import Path
from lib.rofi import rofi
from lib.notifysend import NotifySend

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")

NOTE_PATH = Path.home() / "Notes"
APPNAME = "Simple notepad"


class Notepad(Gtk.Window):
    def __init__(self, filename=None):
        super().__init__(title=APPNAME)
        self.set_wmclass(APPNAME, APPNAME)
        self.set_default_size(800, 600)
        self.set_border_width(6)

        self.filePath = Path(filename)
        try:
            self.fileContent = self.filePath.read_text()
        except:
            self.fileContent = ""

        self.notify = NotifySend().setAppName(APPNAME).setAppName("notepad").setTransient()

        # Apply dark theme
        settings = Gtk.Settings.get_default()
        settings.set_property("gtk-application-prefer-dark-theme", False)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Filename entry (editable)
        self.filename_entry = Gtk.Entry()
        self.filename_entry.set_text(self.windowTitle)
        self.filename_entry.set_placeholder_text("Enter filename here")
        self.filename_entry.set_alignment(0.5)  # 1.0 = right, 0.0 = left, 0.5 = center
        vbox.pack_start(self.filename_entry, False, False, 0)

        # Text buffer and view
        lm = GtkSource.LanguageManager()
        self.buffer = GtkSource.Buffer()
        self.buffer.set_language(lm.get_language("bash"))

        self.view = GtkSource.View.new_with_buffer(self.buffer)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view.set_show_line_numbers(True)
        self.view.set_monospace(True)
        self.buffer.set_text(self.fileContent)

        # Scrolled window
        scroll = Gtk.ScrolledWindow()
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        scroll.add(self.view)

        # Buttons
        save_btn = Gtk.Button(label="💾 Save")
        save_btn.connect("clicked", self.save)

        cancel_btn = Gtk.Button(label="❌ Cancel")
        cancel_btn.connect("clicked", self.cancel)

        del_btn = Gtk.Button(label="❌ Delete")
        del_btn.connect("clicked", self.delete_file)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_box.pack_start(save_btn, False, False, 0)
        btn_box.pack_start(cancel_btn, False, False, 0)
        btn_box.pack_end(del_btn, False, False, 1)

        # Layout
        vbox.pack_start(scroll, True, True, 0)
        vbox.pack_start(btn_box, False, False, 0)

        self.add(vbox)
        self.connect("destroy", Gtk.main_quit)
        self.connect("delete-event", self.on_delete_event)
        self.connect("key-press-event", self.on_key_press)

        GLib.idle_add(self.filename_entry.set_position, -1)
        GLib.idle_add(self.view.grab_focus)

    @property
    def windowTitle(self):
        return self.filePath.name if str(NOTE_PATH) in str(self.filePath) else str(self.filePath)

    def get_current_content(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, True)

    def is_content_changed(self):
        return self.fileContent != self.get_current_content()

    def on_filename_changed(self, entry):
        fileName = entry.get_text()
        self.filePath = Path(fileName) if "/" in fileName else NOTE_PATH / fileName
        if self.filePath.name:
            self.set_title(os.path.basename(self.filePath))

    def save(self, _widget=None):
        fileName = self.filename_entry.get_text().strip()
        if not fileName:
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Filename is required!",
            )
            dialog.format_secondary_text("Please enter a valid filename before saving.")
            dialog.run()
            dialog.destroy()
            return

        self.filePath = Path(fileName) if "/" in fileName else NOTE_PATH / fileName
        if self.filePath.is_dir():
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Saved path is a directory, not a file",
            )
            dialog.format_secondary_text("Please enter a valid filename before saving.")
            dialog.run()
            dialog.destroy()
            return

        if self.filePath.name:
            text = self.get_current_content()
            self.filePath.write_text(text)
            self.notify.setTitle("Saved").setMessage(self.filePath).flash()
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
            filePath = Path(dialog.get_filename())
            text = self.get_current_content()
            filePath.write_text(text)
            self.notify.setTitle("Saved").setMessage(filePath).flash()
        dialog.destroy()

    def delete_file(self, _widget=None):
        if not self.filePath:
            return
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Delete file?",
        )
        dialog.format_secondary_text(str(self.filePath))
        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.OK:
            try:
                os.remove(self.filePath)
            except FileNotFoundError:
                pass
            self.notify.setTitle("Deleted note").setMessage(self.filePath).flash()
            print("File deleted:", self.filePath)
            Gtk.main_quit()

    def on_key_press(self, widget, event):
        keyval = event.keyval
        state = event.state

        ctrl = state & Gdk.ModifierType.CONTROL_MASK
        shift = state & Gdk.ModifierType.SHIFT_MASK

        if keyval == Gdk.KEY_Escape:
            self.close()
        elif ctrl and shift and keyval == Gdk.KEY_S:
            self.save_as()
        elif ctrl and keyval == Gdk.KEY_Delete:
            self.delete_file()

    def on_delete_event(self, widget, event):
        if self.is_content_changed():  # Use your logic here
            return self.show_exit_confirmation()
        return False  # allow the window to close

    def show_exit_confirmation(self):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text="Do you want to save changes before quitting?",
        )
        dialog.format_secondary_text("Your changes will be lost if you don’t save them.")
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Don't Save", Gtk.ResponseType.NO)
        dialog.add_button("Save", Gtk.ResponseType.YES)

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self.save()
            return False  # allow quit
        elif response == Gtk.ResponseType.NO:
            return False  # allow quit
        else:
            return True  # cancel quit


def rofiSelectNote():
    rf = rofi('-theme', 'overlays/center-dialog').makeDmenu()
    for item in NOTE_PATH.iterdir():
        rf.addItem(item.name, "note")
    rf.addItem("New", "note-add")
    return rf.run()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        path = rofiSelectNote()

    if not (Path(path).exists() and Path(path).parent.exists()):
        path = str(NOTE_PATH / path)
    win = Notepad(filename=path)
    win.show_all()
    Gtk.main()
