from db_connection import DBConnection 

class InventoryDAO:
    def __init__(self):
        self.db = DBConnection().connect()

    def add_book_copy_to_stock(self, barcode, isbn, location=None, book_condition="Mới"):
        """1. Nhập thêm một cuốn sách (bản sao) vào kho theo mã ISBN và Barcode riêng"""
        try:
            cursor = self.db.cursor()
            query = """
                INSERT INTO bookcopy (barcode, status, book_condition, ISBN) 
                VALUES (%s, 'Available', %s, %s)
            """
            cursor.execute(query, (barcode, book_condition, isbn))
            self.db.commit()
            print(f"-> Đã nhập kho thành công bản sao sách có mã vạch: {barcode}")
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Lỗi nhập kho: {e}")
            return False

    def update_book_status(self, barcode, new_status):
        """2. Cập nhật trạng thái sách (Ví dụ: 'Available', 'Borrowed', 'Lost')"""
        try:
            cursor = self.db.cursor()
            query = "UPDATE bookcopy SET status = %s WHERE barcode = %s"
            cursor.execute(query, (new_status, barcode))
            self.db.commit()
            print(f"-> Đã cập nhật trạng thái cuốn sách {barcode} thành '{new_status}'.")
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Lỗi cập nhật trạng thái: {e}")
            return False

    def get_inventory_report(self):
        """3. Thống kê báo cáo số lượng sách hiện có trong kho (Available) theo từng đầu sách"""
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
                SELECT b.ISBN, b.title, COUNT(bc.barcode) AS quantity_in_stock
                FROM bookcopy bc
                JOIN book b ON bc.ISBN = b.ISBN
                WHERE bc.status = 'Available'
                GROUP BY b.ISBN, b.title
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Lỗi lấy báo cáo kho: {e}")
            return []