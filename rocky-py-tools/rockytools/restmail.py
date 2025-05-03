
from lib.rofi import rofi
from pathlib import Path
from lib.restmail import RestMailClient

STOREAGE = Path.home() / "restmail"


class RofiMailFE:
    def __init__(self):
        self.cursor = STOREAGE
        self.rofi = rofi('-dmenu', '-theme', 'overlays/thin-side-bar', '-icon-theme', 'rofi',
                         '-p', 'Restmail', '-theme+inputbar+children', '[ prompt, entry ]')

    def listUser(self):
        self.rofi.makeDmenu()
        for item in STOREAGE.iterdir():
            if item.is_dir():
                self.rofi.addItem(item.name, 'user-mail')

        self.rofi.sortMenu().addItem('Add user', 'add-user', 0)
        selected = self.rofi.run()

        if selected == "Add user":
            import tkinter as tk
            from tkinter import simpledialog

            root = tk.Tk()
            root.withdraw()  # Hide the main window

            user_input = simpledialog.askstring("Input", "Enter something:")
            RestMailClient(user_input).makeStorage()
            self.listUser()
            return self

        self.cursor = RestMailClient(selected)
        return self

    def listMail(self):
        self.rofi.makeDmenu()
        for item in self.cursor.listLocalMails():
            self.rofi.addItem(item.name, "email")
        self.rofi.sortMenu()
        self.rofi.addItem('Fetch', 'download')
        self.rofi.addItem('Delete this user', 'del-user')
        self.rofi.addItem('Back', 'back')
        select = self.rofi.run()
        if select == "Back":
            self.listUser().listMail()
            return self
        if select == "Delete this user":
            self.cursor.deleteThisUser()
            self.listUser().listMail()
            return self
        if select == "Fetch":
            self.cursor.fectchMail()
            self.listMail()
            return self
        self.cursor.openLocalMail(select)


def main():
    rfm = RofiMailFE()
    rfm.listUser().listMail()
