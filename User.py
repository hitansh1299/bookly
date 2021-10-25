import sqlite3
class User:
    def __init__(self, username) -> None:
        con = sqlite3.connect("Users.db")
        x = con.execute(f"SELECT * FROM Users WHERE username = '{username}'")
        user = x.fetchone()
        self.username = user[0]
        self.password = user[1]
        self.email = user[2]
        self.phone = user[3]
        self.first_name = user[4]
        self.last_name = user[5]

    def get_as_dict(self) -> {str,str}:
        return self.__dict__
