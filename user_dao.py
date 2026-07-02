from db_connection import DBConnection

class UserDAO:
    def __init__(self):
        self.db = DBConnection().connect()

    def check_login(self, username, password):
        """Hàm kiểm tra đăng nhập (đáp ứng kịch bản test TC01, TC02)"""
        try:
            cursor = self.db.cursor(dictionary=True) 
            
            query = "SELECT * FROM User WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            
            user = cursor.fetchone()
            cursor.close()
            
            if user:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Lỗi khi thực hiện truy vấn: {e}")
            return False

    def register_user(self, username, password, full_name, email):
        """Hàm đăng ký người dùng mới (đáp ứng kịch bản test TC03)"""
        try:
            cursor = self.db.cursor()
            query = "INSERT INTO User (username, password, fullName, email) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, password, full_name, email))
            
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Lỗi khi thêm user: {e}")
            self.db.rollback()
            return False