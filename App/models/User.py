from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, fullname, profesion):
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname
        self.profesion = profesion

    @staticmethod
    def from_mongo(user_data):
        return User(
            id=str(user_data["_id"]),
            username=user_data["email"],
            password=user_data["password"],
            fullname=user_data["fullname"],
            profesion=user_data["profesion"]
        )
