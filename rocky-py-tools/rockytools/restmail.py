import requests
import json
import subprocess as sp
from rockytools import rofi
from pathlib import Path

STOREAGE = Path.home() / "restmail"


class RestMailClient:
    def __init__(self, mailAddr):
        address = mailAddr.split("@")
        self.user = address[0]
        self.storage = STOREAGE / self.user
        try:
            self.url = f"https://{address[1]}"
        except IndexError:
            self.url = "https://restmail.net"

    def fectchMail(self):
        r = requests.get(f"{self.url}/mail/{self.user}")
        mails = r.json()
        for m in mails:
            subj = m["subject"].replace(" ", '.')
            date = m['date']
            filename = f"{subj}_{date}"
            try:
                content = m['html']
                filename += ".html"
            except KeyError:
                content = m['text']
                filename += ".txt"
            file = self.storage / filename
            file.write_text(str(content))
        return self

    def listLocalMails(self):
        return sorted([item for item in self.storage.iterdir()])

    def openLocalMail(self, file):
        file = self.storage / file
        sp.Popen(['xdg-open', str(file.absolute())])
        return self

    def deleteThisUser(self):
        for f in self.storage.iterdir():
            f.unlink()
        self.storage.rmdir()
        return self

    def makeStorage(self):
        self.storage.mkdir()
        return self


class RofiMailFE:
    def __init__(self):
        self.cursor = STOREAGE
        self.rofi = rofi('-dmenu', '-theme', 'overlays/thin-side-bar', '-icon-theme', 'rofi',
                         '-p', 'Restmail', '-theme+inputbar+children', '[ prompt, entry ]')

    def listUser(self):
        self.rofi.newMenu()
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
        self.rofi.newMenu()
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
