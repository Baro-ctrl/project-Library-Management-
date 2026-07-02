from db_connection import DBConnection

class BookDAO:
    def __init__(self):
        self.db = DBConnection().connect()

    def get_all_books(self):
        """Lấy danh sách toàn bộ đầu sách trong thư viện"""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
                SELECT b.ISBN, b.title, b.author, b.publisher, b.publishYear, c.name as category_name 
                FROM Book b 
                LEFT JOIN Category c ON b.categoryId = c.categoryId
            """
            cursor.execute(query)
            books = cursor.fetchall()
            cursor.close()
            return books
        except Exception as e:
            print(f"Lỗi khi lấy danh sách sách: {e}")
            return []

    def add_book(self, isbn, title, author, publisher, year, category_id):
        """Thêm một đầu sách mới vào kho"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO Book (ISBN, title, author, publisher, publishYear, categoryId) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (isbn, title, author, publisher, year, category_id))
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Lỗi khi thêm sách: {e}")
            self.db.rollback()
            return False

    def update_book(self, isbn, title, author, publisher, year, category_id):
        """Cập nhật thông tin của một đầu sách dựa vào ISBN"""
        try:
            cursor = self.db.cursor()
            query = """
                UPDATE Book 
                SET title = %s, author = %s, publisher = %s, publishYear = %s, categoryId = %s 
                WHERE ISBN = %s
            """
            cursor.execute(query, (title, author, publisher, year, category_id, isbn))
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật sách: {e}")
            self.db.rollback()
            return False

    def delete_book(self, isbn):
        """Xóa một đầu sách khỏi hệ thống"""
        try:
            cursor = self.db.cursor()
            query = "DELETE FROM Book WHERE ISBN = %s"
            cursor.execute(query, (isbn,))
            self.db.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Lỗi khi xóa sách: {e}")
            self.db.rollback()
            return False

    def search_book_by_title(self, keyword):
        """Tìm kiếm sách theo tên (hỗ trợ tìm kiếm gần đúng)"""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = "SELECT * FROM Book WHERE title LIKE %s"
            search_pattern = f"%{keyword}%"
            cursor.execute(query, (search_pattern,))
            books = cursor.fetchall()
            cursor.close()
            return books
        except Exception as e:
            print(f"Lỗi khi tìm kiếm sách: {e}")
            return []