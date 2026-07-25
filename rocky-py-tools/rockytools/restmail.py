
from lib.fuzzel import fuzzel
from pathlib import Path
from lib.restmail import RestMailClient

STORAGE = Path.home() / "restmail"
DEL_USER = "Delete this user"
DEL_ALL_MAIL = "Delete all local emails"


class RofiMailFE:
    def __init__(self):
        self.cursor: RestMailClient
        self.fuzzel = fuzzel().makeDmenu().setPrompt("Restmail ").setAnchor("right")

    def listUser(self):
        self.fuzzel.makeDmenu()
        for item in STORAGE.iterdir():
            if item.is_dir():
                self.fuzzel.addItem(item.name, 'user-mail')

        self.fuzzel.sortDmenu().addItem('Add user', 'add-user', 0)
        selected = self.fuzzel.run()

        if selected == "Add user":
            user_input = fuzzel().makeDmenu().setPrompt("New user: ").run().replace(" ", '.')
            RestMailClient(user_input).makeStorage()
            self.listUser()
            return self

        self.cursor = RestMailClient(selected)
        return self

    def listMail(self):
        self.fuzzel.makeDmenu()
        for item in self.cursor.listLocalMails():
            self.fuzzel.addItem(item.name, "email")
        self.fuzzel.sortDmenu()
        self.fuzzel.addItem('Fetch', 'download')
        self.fuzzel.addItem(DEL_ALL_MAIL, 'delete')
        self.fuzzel.addItem(DEL_USER, 'del-user')
        self.fuzzel.addItem('Back', 'back')
        select = self.fuzzel.run()
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
