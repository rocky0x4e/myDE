#!/usr/bin/env python3

import requests
import json
import subprocess as sp

from pathlib import Path

STOREAGE = Path.home() / "restmail"
I='\\x00icon\\x1f'

class JsonMail:
    def __init__(self,jsondata):
        if type(jsondata) == dict:
            self.jsondata = jsondata
        else:
            self.jsondata = json.loads(jsondata)

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
            subj = m["subject"].replace(" ",'.')
            date = m['date']
            filename = f"{subj}_{date}"
            try:
                content = m['html']
                filename += ".html"
            except KeyError:
                content = m['text']
                filename += ".txt"
            file=self.storage / filename
            file.write_text(str(content))
        return self

    def listLocalMails(self):
        return [item for item in self.storage.iterdir()]

    def openLocalMail(self, file):
        file = self.storage / file
        sp.Popen(['xdg-open',str(file.absolute())])
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

    def _rofiMenu(self, menu):
        echo = sp.Popen(['echo', '-en', '\n'.join(menu)], stdout=sp.PIPE, stderr=sp.PIPE)
        try:
            return sp.check_output(['rofi','-dmenu','-theme', 'overlays/thin-side-bar', '-icon-theme', 'rofi',
                         '-p', 'Restmail', '-theme+inputbar+children' ,'[ prompt, entry ]'], stdin=echo.stdout).decode().strip()
        except sp.CalledProcessError:
            exit(0)

    def listUser(self):
        menu=[]
        for item in STOREAGE.iterdir():
            if item.is_dir():
                menu.append(f'{item.name}{I}user-mail')

        menu = sorted(menu)
        menu.insert(0, f'Add user{I}add-user')

        selected = self._rofiMenu(menu)
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
        menu = []
        for item in self.cursor.listLocalMails():
            menu.append(f"{item.name}{I}email")
        menu += [f'Fetch{I}download',f'Delete this user{I}del-user',f'Back{I}back']
        select = self._rofiMenu(menu)
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


rfm =  RofiMailFE()

rfm.listUser().listMail()
