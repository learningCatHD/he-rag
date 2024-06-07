import pymysql as mysql
import os

class SqlBase:
    def __init__(self):
        self.host = os.environ.get("HOST")
        self.user = os.environ.get("USER")
        self.password = os.environ.get("PASSWORD")
        self.database = os.environ.get("DATABASE")
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
        except mysql.connect.Error as e:
            print(f"Error connecting to database: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:  
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except mysql.connect.Error as e:
            print(f"Error executing query: {e}")
            return None

    def insert(self, table_name, data):
        try:
            columns = ', '.join(data.keys())
            values = tuple(data.values())
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({','.join(['%s'] * len(data))})"
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connect.Error as e:
            print(f"Error inserting data: {e}")
            return None

if __name__=="__main__":

    # 创建 MySQLManager 实例
    mysql_manager = SqlBase()

    # 连接数据库
    mysql_manager.connect()

    # 查询 user_info 表的全部内容
    results = mysql_manager.query("SELECT * FROM user_info")
    for row in results:
        print(row)

    # # 插入数据到 user_info 表
    # new_user = {
    #     "name": "John Doe",
    #     "email": "john.doe@example.com"
    # }
    # new_user_id = mysql_manager.execute_insert("user_info", new_user)
    # print(f"New user ID: {new_user_id}")

    # 断开数据库连接
    mysql_manager.disconnect()