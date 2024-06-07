
from plato.collector import SqlBase
import uuid

class UserProfile:
    def __init__(self) -> None:
        self.db = SqlBase()
        self.table = "user_info"
        
    def _register(self, username, email, gender, career, password, other=None):
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