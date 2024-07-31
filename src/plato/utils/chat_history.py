from dotenv import load_dotenv


load_dotenv()
import os
import redis
import  pickle
REDIS_URI = os.environ.get('REDIS_URI')

class chat_history():
    def __init__(self):
        R = redis.ConnectionPool(host='localhost', port=REDIS_URI.split(':')[-1])
        self.datebase = redis.Redis(connection_pool=R)
        self.name = "chat-history"

    def history_exit(self,uid):
        return self.datebase.hexists(self.name,uid)

    def get_history(self,uid):
        if self.history_exit(uid):
            his = self.datebase.hget(self.name,uid)
            return pickle.loads(his)
        else:
            return []


    def set_history(self,uid,his):
        self.datebase.hset(self.name,uid,pickle.dumps(his))