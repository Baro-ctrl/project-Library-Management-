from borrow_dao import BorrowDAO
from db_connection import DBConnection

borrow_dao = BorrowDAO()

print("--- TEST CHỨC NĂNG MƯỢN SÁCH ---")
is_success = borrow_dao.create_borrow_slip("PM-002", "R001", None, ["BC-001"])

if is_success:
    print("Thành công: Đã tạo phiếu mượn và cập nhật kho sách!")
else:
    print("Thất bại: Có lỗi xảy ra trong quá trình mượn.")

DBConnection().close()