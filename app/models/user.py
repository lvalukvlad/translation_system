class User:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.username = username
        self.role = role

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Translator(User):
    def __init__(self, user_size, username):
        super().__init__(user_size, username, 'translator')


class Editor(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'editor')


class Admin(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'admin')