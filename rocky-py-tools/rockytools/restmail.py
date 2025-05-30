
from lib.rofi import rofi
from pathlib import Path
from lib.restmail import RestMailClient

STOREAGE = Path.home() / "restmail"
DEL_USER = "Delete this user"
DEL_ALL_MAIL = "Delete all local emails"


class RofiMailFE:
    def __init__(self):
        self.cursor = STOREAGE
        self.rofi = rofi().setInputBarChildren('[ prompt, entry ]')\
            .makeDmenu().setTheme('overlays/thin-side-bar').setPrompt("Restmail")

    def listUser(self):
        self.rofi.makeDmenu()
        for item in STOREAGE.iterdir():
            if item.is_dir():
                self.rofi.addItem(item.name, 'user-mail')

        self.rofi.sortDmenu().addItem('Add user', 'add-user', 0)
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
        self.rofi.sortDmenu()
        self.rofi.addItem('Fetch', 'download')
        self.rofi.addItem(DEL_ALL_MAIL, 'delete')
        self.rofi.addItem(DEL_USER, 'del-user')
        self.rofi.addItem('Back', 'back')
        select = self.rofi.run()
        if select == "Back":
            self.listUser().listMail()
            return self
        if select == DEL_USER:
            self.cursor.deleteThisUser()
            self.listUser().listMail()
            return self
        if select == DEL_ALL_MAIL:
            self.cursor.deleteAllLocalMails()
            self.listMail()
            return self
        if select == "Fetch":
            self.cursor.fectchMail()
            self.listMail()
            return self
        self.cursor.openLocalMail(select)


def main():
    rfm = RofiMailFE()
    rfm.listUser().listMail()
