from gi.repository import Gtk, GtkSource, Gdk, GLib, WebKit2  # type: ignore
import markdown
import gi
import sys
import os
from pathlib import Path
from lib.rofi import rofi
from lib.notification import DefautNotifier

gi.require_version("Gtk", "3.0")
gi.require_version("GtkSource", "4")

NOTE_PATH = Path.home() / "Notes"
APPNAME = "Simple notepad"


class Notepad(Gtk.Window):
    def __init__(self, filename=None):
        super().__init__(title=APPNAME)
        GLib.idle_add(self.show_preview_by_default)
        self.set_wmclass(APPNAME, APPNAME)
        self.set_default_size(800, 600)
        self.set_border_width(6)
        hint = Gtk.Label(label=("💾 Ctrl+S: Edit/Save  |  💾 Ctrl+Shift+S: Save -> quit\n"
                                "❌ ESC: Quit  |   Ctrl+Del: Delete & quit"))
        hint.set_xalign(0.5)  # Align left (optional)
        hint.set_justify(Gtk.Justification.CENTER)
        icon = Gtk.Image.new_from_icon_name("dialog-information", Gtk.IconSize.DIALOG)
        hint_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hint_box.set_halign(Gtk.Align.CENTER)
        hint_box.pack_start(icon, False, False, 0)
        hint_box.pack_start(hint, False, False, 0)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_name("thick-separator")
        css = b"""
        #thick-separator {
            min-height: 2px;
            background-color: #555;  /* Optional: give it a visible color */
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.notify = DefautNotifier().setAppName(APPNAME).setAppName("notepad").setTransient()

        self.filePath = Path(filename)
        try:
            self.fileContent = self.filePath.read_text()
        except Exception as e:
            self.notify.setTitle("Error").setMessage(str(e)).flash()
            self.fileContent = ""

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
        self.buffer.set_language(lm.get_language("markdown"))

        self.textView = GtkSource.View.new_with_buffer(self.buffer)
        self.textView.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textView.set_show_line_numbers(True)
        self.textView.set_monospace(True)

        self.textView.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textView.set_show_line_numbers(True)
        self.textView.set_monospace(True)
        self.buffer.set_text(self.fileContent)
        self.buffer.connect("changed", self.on_content_changed)

        # markdown support
        self.webview = WebKit2.WebView()
        self.webview.set_visible(False)
        self.webview.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.webview.connect("button-press-event", self.on_webview_click)
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(200)
        # Preview
        preview_scroll = Gtk.ScrolledWindow()
        preview_scroll.set_hexpand(True)
        preview_scroll.set_vexpand(True)
        preview_scroll.add(self.webview)
        self.stack.add_named(preview_scroll, "preview")
        self.stack.set_visible_child_name("preview")

        # Editor
        editor_scroll = Gtk.ScrolledWindow()
        editor_scroll.set_hexpand(True)
        editor_scroll.set_vexpand(True)
        editor_scroll.add(self.textView)
        self.stack.add_named(editor_scroll, "editor")

        # Buttons
        self.btnSave = Gtk.ToggleButton(label=" Edit")
        self.btnSave.connect("toggled", self.toggle_preview)
        self.btnSaveAs = Gtk.Button(label="💾 Save as")
        self.btnSaveAs.connect("clicked", self.save_as)

        btnCancel = Gtk.Button(label="❌ Cancel")
        btnCancel.connect("clicked", self.cancel)
        btnDel = Gtk.Button(label=" Delete")
        btnDel.connect("clicked", self.delete_file)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        btn_box.pack_start(self.btnSave, False, False, 0)
        btn_box.pack_start(btnCancel, False, False, 0)
        btn_box.pack_end(btnDel, False, False, 1)
        btn_box.pack_end(self.btnSaveAs, False, False, 0)

        # Layout
        vbox.pack_start(self.stack, True, True, 0)
        vbox.pack_start(hint_box, False, False, 0)
        vbox.pack_start(separator, False, True, 6)
        vbox.pack_start(btn_box, False, False, 0)

        self.add(vbox)
        self.connect("destroy", Gtk.main_quit)
        self.connect("delete-event", self.on_delete_event)
        id = self.connect("key-press-event", self.on_key_press)
        self.webview.disconnect(id)

        GLib.idle_add(self.filename_entry.set_position, -1)
        GLib.idle_add(self.textView.grab_focus)
        self.show_all()
        # self.saveas_btn.hide()

    @property
    def windowTitle(self):
        return self.filePath.name if str(NOTE_PATH) in str(self.filePath) else str(self.filePath)

    def show_preview_by_default(self):
        self.stack.set_visible_child_name("preview")
        self.update_preview()
        return False  # Stop repeating the idle function

    def toggle_preview(self, button):
        if button.get_active():
            self.stack.set_visible_child_name("editor")
            button.set_label("Done")
        else:
            self.update_preview()
            self.save() if "Save" in self.btnSave.get_label() else None
            self.stack.set_visible_child_name("preview")
            button.set_label(" Edit")

    def update_preview(self):
        start, end = self.buffer.get_bounds()
        markdown_text = self.buffer.get_text(start, end, True)
        html = markdown.markdown(markdown_text)
        self.webview.load_html(html, "file:///")

    def get_current_content(self):
        start, end = self.buffer.get_bounds()
        return self.buffer.get_text(start, end, True)

    def is_content_changed(self):
        return self.fileContent != self.get_current_content()

    def on_content_changed(self, entry):
        if self.is_content_changed():
            self.btnSave.set_label("💾 Save")
        else:
            self.btnSave.set_label("Done")

    def on_webview_click(self, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            self.btnSave.emit("clicked")

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
            self.fileContent = text
            self.notify.setTitle("Saved").setMessage(self.filePath).flash()

    def cancel(self, _widget=None):
        Gtk.main_quit()

    def save_and_quit(self, _widget=None):
        self.save()
        self.cancel()

    def save_as(self, _widget=None):
        dialog = Gtk.FileChooserDialog(
            title="Save As",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        )
        dialog.set_do_overwrite_confirmation(True)

        if dialog.run() == Gtk.ResponseType.OK:
            self.filePath = Path(dialog.get_filename())
            text = self.get_current_content()
            self.filePath.write_text(text)
            self.fileContent = text
            self.notify.setTitle("Saved").setMessage(self.filePath).flash()
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
            child = self.stack.get_visible_child_name()
            if child == 'editor':
                self.btnSave.emit("clicked")
            else:
                self.close()

        elif ctrl and not shift and keyval in [Gdk.KEY_s, Gdk.KEY_S]:
            # self.save()
            self.btnSave.emit("clicked")
        elif ctrl and shift and keyval in [Gdk.KEY_s, Gdk.KEY_S]:
            self.save_and_quit()
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
    rf = rofi({'-theme+listview+columns': '1'}).makeDmenu().setTheme('overlays/center-dialog').setPrompt("Notes")
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
    Gtk.main()
