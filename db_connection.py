import mysql.connector
from mysql.connector import Error

class DBConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
            cls._instance.connection = None
        return cls._instance

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host='localhost',
                    database='library_management',
                    user='root',
                    password='123456'     
                )
                print("Đã kết nối thành công tới cơ sở dữ liệu MySQL!")
            except Error as e:
                print(f"Lỗi kết nối MySQL: {e}")
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Đã đóng kết nối MySQL an toàn.")