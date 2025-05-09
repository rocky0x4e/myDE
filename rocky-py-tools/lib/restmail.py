import requests
import subprocess as sp
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

    def deleteAllLocalMails(self):
        for f in self.storage.iterdir():
            f.unlink()
        return self
