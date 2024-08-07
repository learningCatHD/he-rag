
from plato.collector import SqlBase
import uuid

class UserProfile:
    def __init__(self) -> None:
        self.db = SqlBase()
        self.table = "user_info"

    def _register(self, username, email, gender, career, password, other=None):

        existing_user = self.db.query(
            f"SELECT * FROM {self.table} WHERE email = %s", (email,)
        )
        if existing_user:
            return "-1", f"User with email {email} already exists!"

        uid = str(uuid.uuid4())
        user_data = {
            "uid": uid,
            "username": username,
            "email": email,
            "gender": gender,
            "career": career,
            "password": password
        }
        try:
            self.db.insert(
                self.table, user_data
            )
        except Exception as e:
            print(e)
        return uid, f"user {username} created !"
    
    def _query(self, uid):
        try:
            query = f"SELECT uid = {uid} FROM user_info"
            result = self.db.query(
                query=query
            )
        except Exception as e:
            print(e)
        return result
    
    def _unregister(self, uid):
        try:
            delete_user_query = f"DELETE FROM user_info WHERE uid = '{uid}'"
            result = self.db.query(
                query=delete_user_query
            )
        except Exception as e:
            print(e)
        return result

    def _login(self, username, password):
        try:
            query = f"SELECT uid FROM {self.table} WHERE (username = %s OR email = %s) AND password = %s"
            params = (username, username, password)
            result = self.db.query(query, params)
            if result:
                for row in result:
                    uid = row[0]
                return 0, uid
            else:
                return 1, ''
        except Exception as e:
            print(e)
            return 2, ''

    def _sendsms(self, phone):
        try:
            query = f"SELECT COUNT(*) FROM {self.table} WHERE phone = %s"
            params = (phone,)
            result = self.db.query(query, params)

            if result and result[0][0] > 0:
                return 0
            else:
                return 1

        except Exception as e:
            print(e)
            return 2

    def _verifysms(self, phone):
        try:
            query = f"SELECT uid FROM {self.table} WHERE phone = %s "
            params = (phone,)
            result = self.db.query(query, params)

            if result:
                for row in result:
                    uid = row[0]
                return "0", uid
            else:
                return "1", ''

        except Exception as e:
            print(e)
            return "2", ''