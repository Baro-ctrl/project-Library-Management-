"""
db_queries.py
------------------------------------------------
File riêng chứa toàn bộ phần kết nối và truy vấn CSDL MySQL (LibraryManagement)
cho ứng dụng Thư Viện Xanh. Tách riêng khỏi file giao diện (thu_vien_xanh_app.py)
để dễ bảo trì: nếu cần đổi thông tin kết nối hoặc sửa câu truy vấn, chỉ cần sửa
trong file này.

Yêu cầu thư viện: mysql-connector-python (pip install mysql-connector-python)

Kết nối database:
    Thông tin kết nối nằm trong DB_CONFIG (host=localhost, user=root,
    password=12345, database=LibraryManagement).
    Ghi chú: "sa1" là tên connection bạn đặt trong MySQL Workbench (chỉ để
    Workbench hiển thị/quản lý, không cần khai báo trong code Python - Python
    kết nối trực tiếp qua host/port/user/password bên dưới). Nếu connection
    "sa1" của bạn trỏ tới host/port khác localhost:3306, hãy sửa lại "host" /
    "port" trong DB_CONFIG cho khớp.

    Hàm fetch_books_by_category() join bảng Books + Author và lọc theo
    categoryId (C001=Tiểu Thuyết, C002=Văn Học, C003=Truyện Tranh, C004=Kinh Dị)
    đúng theo schema trong file LibraryManagement.sql.
    Nếu không kết nối được (thiếu mysql-connector-python, sai thông tin đăng
    nhập, server tắt, v.v...), hàm sẽ trả về dữ liệu mẫu (fallback) được
    truyền vào, để giao diện vẫn chạy.
"""

# mysql-connector-python dùng để kết nối MySQL. Nếu chưa cài
# (pip install mysql-connector-python), chương trình vẫn chạy được bằng dữ
# liệu mẫu (fallback).
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

# ----------------------------------------------------------------------------
# KẾT NỐI DATABASE (MySQL - LibraryManagement)
# Connection name trong MySQL Workbench: sa1
# ----------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "12345",
    "database": "LibraryManagement",
}


def get_db_connection():
    """Tạo kết nối tới MySQL dựa trên DB_CONFIG."""
    return mysql.connector.connect(**DB_CONFIG)


def fetch_books_by_category(category_id, fallback):
    """
    Lấy danh sách sách theo thể loại từ CSDL LibraryManagement.

    category_id: mã categoryId trong bảng Category:
        C001 = Tiểu Thuyết, C002 = Văn Học, C003 = Truyện Tranh, C004 = Kinh Dị

    Join 2 bảng Books + Author theo đúng schema trong LibraryManagement.sql:
        Books(isbn, categoryId, authorId, title, publisher, publishYear, imageUrl, description)
        Author(authorId, authorName, imageUrl, biography)

    Nếu không cài mysql-connector-python, không kết nối được, hoặc câu truy
    vấn lỗi/không có dòng nào khớp, hàm sẽ trả về dữ liệu mẫu (fallback) để
    giao diện vẫn hiển thị bình thường thay vì bị crash.
    """
    if not MYSQL_AVAILABLE:
        print("[Cảnh báo] Chưa cài mysql-connector-python (pip install mysql-connector-python) -> dùng dữ liệu mẫu.")
        return fallback

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT b.imageUrl, b.title, a.authorName, b.publishYear
            FROM Books b
            JOIN Author a ON b.authorId = a.authorId
            WHERE b.categoryId = %s
            ORDER BY b.title
            """,
            (category_id,),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return fallback

        books = []
        for image_url, title, author_name, publish_year in rows:
            books.append({
                "img": (image_url or "").strip(),
                "title": (title or "").strip(),
                "author": (author_name or "").strip(),
                "year": f"({publish_year})" if publish_year else "",
            })
        return books

    except Exception as e:
        print(f"[Cảnh báo] Lỗi khi lấy dữ liệu thể loại '{category_id}' từ CSDL: {e}")
        print("=> Đang dùng dữ liệu mẫu (fallback) để giao diện vẫn chạy được.")
        return fallback
