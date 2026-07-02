from db_connection import DBConnection
from datetime import date, timedelta

class BorrowDAO:
    def __init__(self):
        self.db = DBConnection().connect()

    def create_borrow_slip(self, slip_id, reader_id, employee_id, list_barcodes):
        """
        Nghiệp vụ mượn sách:
        1. Tạo Phiếu mượn (BorrowSlip)
        2. Tạo Chi tiết phiếu mượn (BorrowDetail) cho từng cuốn sách
        3. Đổi trạng thái (status) của sách (BookCopy) thành 'Borrowed'
        """
        try:
            cursor = self.db.cursor()
            
            borrow_date = date.today()
            due_date = borrow_date + timedelta(days=14)
            
            query_slip = """
                INSERT INTO BorrowSlip (slipId, borrowDate, dueDate, status, readerId, employeeId)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query_slip, (slip_id, borrow_date, due_date, 'Active', reader_id, employee_id))
            
            query_detail = """
                INSERT INTO BorrowDetail (slipId, barcode, returnDate, fineAmount, note, renewalCount)
                VALUES (%s, %s, NULL, 0, '', 0)
            """
            query_update_book = "UPDATE BookCopy SET status = 'Borrowed' WHERE barcode = %s"
            
            for barcode in list_barcodes:
                cursor.execute(query_detail, (slip_id, barcode))
                cursor.execute(query_update_book, (barcode,))
            
            self.db.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Lỗi khi thực hiện giao dịch mượn sách: {e}")
            self.db.rollback() 
            return False

    def return_book(self, slip_id, barcode):
        """
        Nghiệp vụ trả sách:
        1. Cập nhật ngày trả (returnDate) vào chi tiết phiếu mượn
        2. Đổi trạng thái sách thành 'Available'
        """
        try:
            cursor = self.db.cursor()
            return_date = date.today()
            
            query_detail = """
                UPDATE BorrowDetail 
                SET returnDate = %s 
                WHERE slipId = %s AND barcode = %s
            """
            cursor.execute(query_detail, (return_date, slip_id, barcode))
            
            query_book = "UPDATE BookCopy SET status = 'Available' WHERE barcode = %s"
            cursor.execute(query_book, (barcode,))
            
            self.db.commit()
            cursor.close()
            return True
            
        except Exception as e:
            print(f"Lỗi khi thực hiện trả sách: {e}")
            self.db.rollback()
            return False