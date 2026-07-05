"""
auth_queries.py
------------------------------------------------
File riêng chứa toàn bộ phần xử lý ĐĂNG NHẬP / ĐĂNG KÝ tài khoản cho ứng dụng
Thư Viện Xanh. Tách riêng khỏi db_queries.py (vốn chỉ lo lấy danh sách sách
theo thể loại) và khỏi phần giao diện (auth_ui.py, thu_vien_xanh_app.py) để
dễ bảo trì.

Schema sử dụng (theo LibraryManagement.sql - bản MySQL):
    `User`(userId, username, password, fullName, email, phone, role)
        role IN ('Admin', 'Reader', 'Librarian')
    Reader(readerId, userId, cardExpiryDate, totalBorrowed)

Tài khoản Admin & Librarian đã được TẠO SẴN trong CSDL (xem phần
INSERT INTO `User` ... trong LibraryManagement.sql), ví dụ:
    admin01 / admin123        (Admin)
    librarian01 / lib123      (Librarian)
Người dùng đăng ký mới từ giao diện chỉ được tạo với vai trò 'Reader'
(Độc giả) và sẽ được thêm 1 dòng tương ứng vào bảng Reader.

Chế độ dự phòng (fallback) khi KHÔNG kết nối được MySQL:
    Toàn bộ tài khoản (kể cả tài khoản đăng ký mới) sẽ được lưu vào 1 file
    JSON cục bộ "local_accounts.json" cạnh file này, để chức năng đăng nhập/
    đăng ký vẫn hoạt động khi demo/test mà không cần bật MySQL Server.
    File này được seed sẵn 2 tài khoản mẫu (Admin, Librarian) giống với dữ
    liệu mẫu trong LibraryManagement.sql.
"""

import os
import json
import datetime

from db_queries import get_db_connection, MYSQL_AVAILABLE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_ACCOUNTS_FILE = os.path.join(BASE_DIR, "local_accounts.json")

# Tài khoản mẫu để seed file cục bộ khi chạy offline (khớp với LibraryManagement.sql)
_SEED_ACCOUNTS = [
    {
        "userId": "U001", "username": "admin01", "password": "admin123",
        "fullName": "Nguyễn Quản Trị", "email": "admin@library.com",
        "phone": "0901000001", "role": "Admin",
    },
    {
        "userId": "U005", "username": "librarian01", "password": "lib123",
        "fullName": "Nguyễn Thủ Thư", "email": "librarian01@library.com",
        "phone": "0901000005", "role": "Librarian",
    },
]


# ----------------------------------------------------------------------------
# LƯU TRỮ CỤC BỘ (FALLBACK) - dùng khi không kết nối được MySQL
# ----------------------------------------------------------------------------
def _load_local_accounts():
    if not os.path.exists(LOCAL_ACCOUNTS_FILE):
        _save_local_accounts(_SEED_ACCOUNTS)
        return [dict(a) for a in _SEED_ACCOUNTS]
    try:
        with open(LOCAL_ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return [dict(a) for a in _SEED_ACCOUNTS]


def _save_local_accounts(accounts):
    try:
        with open(LOCAL_ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Cảnh báo] Không lưu được local_accounts.json: {e}")


def _next_local_user_id(accounts):
    max_num = 0
    for acc in accounts:
        uid = acc.get("userId", "")
        if uid.startswith("U") and uid[1:].isdigit():
            max_num = max(max_num, int(uid[1:]))
    return f"U{max_num + 1:03d}"


# ----------------------------------------------------------------------------
# ĐĂNG KÝ (chỉ tạo tài khoản vai trò 'Reader')
# ----------------------------------------------------------------------------
def register_reader(username, contact, password, full_name=None):
    """
    Đăng ký tài khoản mới, vai trò mặc định là 'Reader' (Độc giả).
    Admin/Librarian không đăng ký qua giao diện này (đã có sẵn trong CSDL).

    username : tên đăng nhập
    contact  : email hoặc số điện thoại (tự nhận diện qua ký tự '@')
    password : mật khẩu
    full_name: họ tên hiển thị (nếu bỏ trống sẽ dùng tạm username)

    Trả về dict: {"success": bool, "message": str, "user": dict | None}
    """
    username = (username or "").strip()
    contact = (contact or "").strip()
    password = (password or "").strip()
    full_name = (full_name or username).strip()

    if not username or not contact or not password:
        return {"success": False, "message": "Vui lòng nhập đầy đủ thông tin.", "user": None}

    email = contact if "@" in contact else None
    phone = contact if "@" not in contact else None

    if MYSQL_AVAILABLE:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM `User` WHERE username = %s "
                "OR (email IS NOT NULL AND email = %s) "
                "OR (phone IS NOT NULL AND phone = %s)",
                (username, email, phone),
            )
            if cursor.fetchone()[0] > 0:
                cursor.close()
                conn.close()
                return {"success": False,
                        "message": "Tên đăng nhập / email / số điện thoại đã được sử dụng.",
                        "user": None}

            cursor.execute("SELECT userId FROM `User`")
            max_num = 0
            for (uid,) in cursor.fetchall():
                if uid and uid.startswith("U") and uid[1:].isdigit():
                    max_num = max(max_num, int(uid[1:]))
            new_user_id = f"U{max_num + 1:03d}"

            cursor.execute(
                "INSERT INTO `User` (userId, username, password, fullName, email, phone, role) "
                "VALUES (%s, %s, %s, %s, %s, %s, 'Reader')",
                (new_user_id, username, password, full_name, email, phone),
            )

            cursor.execute("SELECT readerId FROM Reader")
            max_r = 0
            for (rid,) in cursor.fetchall():
                if rid and rid.startswith("R") and rid[1:].isdigit():
                    max_r = max(max_r, int(rid[1:]))
            new_reader_id = f"R{max_r + 1:03d}"

            expiry = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
            cursor.execute(
                "INSERT INTO Reader (readerId, userId, cardExpiryDate, totalBorrowed) "
                "VALUES (%s, %s, %s, 0)",
                (new_reader_id, new_user_id, expiry),
            )

            conn.commit()
            cursor.close()
            conn.close()

            user = {"userId": new_user_id, "username": username, "fullName": full_name,
                    "email": email, "phone": phone, "role": "Reader"}
            return {"success": True, "message": "Tạo tài khoản thành công!", "user": user}

        except Exception as e:
            print(f"[Cảnh báo] Lỗi khi đăng ký vào CSDL: {e}")
            print("=> Chuyển sang lưu tài khoản cục bộ (local_accounts.json).")

    # ---- fallback: lưu tài khoản cục bộ ----
    accounts = _load_local_accounts()
    for acc in accounts:
        if (acc["username"] == username
                or (email and acc.get("email") == email)
                or (phone and acc.get("phone") == phone)):
            return {"success": False,
                    "message": "Tên đăng nhập / email / số điện thoại đã được sử dụng.",
                    "user": None}

    new_id = _next_local_user_id(accounts)
    new_account = {"userId": new_id, "username": username, "password": password,
                   "fullName": full_name, "email": email, "phone": phone, "role": "Reader"}
    accounts.append(new_account)
    _save_local_accounts(accounts)

    user = {k: v for k, v in new_account.items() if k != "password"}
    return {"success": True, "message": "Tạo tài khoản thành công! (chế độ cục bộ - chưa nối CSDL)",
            "user": user}


# ----------------------------------------------------------------------------
# ĐĂNG NHẬP
# ----------------------------------------------------------------------------
def login_user(identifier, password):
    """
    Đăng nhập bằng username / email / số điện thoại + mật khẩu.
    identifier có thể là username, email hoặc số điện thoại.

    Trả về dict thông tin user (userId, username, fullName, email, phone, role)
    nếu đúng, hoặc None nếu sai thông tin.
    """
    identifier = (identifier or "").strip()
    password = (password or "").strip()
    if not identifier or not password:
        return None

    if MYSQL_AVAILABLE:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT userId, username, fullName, email, phone, role FROM `User` "
                "WHERE (username = %s OR email = %s OR phone = %s) AND password = %s",
                (identifier, identifier, identifier, password),
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return {"userId": row[0], "username": row[1], "fullName": row[2],
                        "email": row[3], "phone": row[4], "role": row[5]}
            return None
        except Exception as e:
            print(f"[Cảnh báo] Lỗi khi đăng nhập vào CSDL: {e}")
            print("=> Chuyển sang kiểm tra tài khoản cục bộ (local_accounts.json).")

    accounts = _load_local_accounts()
    for acc in accounts:
        if ((acc["username"] == identifier
             or acc.get("email") == identifier
             or acc.get("phone") == identifier)
                and acc["password"] == password):
            return {k: v for k, v in acc.items() if k != "password"}
    return None


# ----------------------------------------------------------------------------
# ĐỔI MẬT KHẨU
# ----------------------------------------------------------------------------
def change_password(user_id, old_password, new_password):
    """
    Đổi mật khẩu cho tài khoản đã đăng nhập, xác định theo userId.

    - Kiểm tra mật khẩu hiện tại (old_password) có khớp với mật khẩu đang lưu
      trong CSDL (bảng `User`, cột password) hay không.
    - Nếu đúng -> cập nhật mật khẩu mới (new_password) và trả về success=True.
    - Nếu sai -> trả về success=False kèm thông báo lỗi phù hợp.
    - Nếu không kết nối được MySQL -> tự động chuyển sang kiểm tra/đổi mật
      khẩu trong file cục bộ local_accounts.json (giống cơ chế của
      login_user / register_reader ở trên).

    Trả về dict: {"success": bool, "message": str}
    """
    user_id = (user_id or "").strip()
    old_password = (old_password or "").strip()
    new_password = (new_password or "").strip()

    if not user_id:
        return {"success": False, "message": "Không xác định được tài khoản. Vui lòng đăng nhập lại."}
    if not old_password or not new_password:
        return {"success": False, "message": "Vui lòng nhập đầy đủ thông tin."}

    if MYSQL_AVAILABLE:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM `User` WHERE userId = %s", (user_id,))
            row = cursor.fetchone()

            if not row:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Không tìm thấy tài khoản."}

            if row[0] != old_password:
                cursor.close()
                conn.close()
                return {"success": False, "message": "Mật khẩu hiện tại không đúng. Vui lòng thử lại."}

            cursor.execute(
                "UPDATE `User` SET password = %s WHERE userId = %s",
                (new_password, user_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
            return {"success": True, "message": "Đổi mật khẩu thành công!"}

        except Exception as e:
            print(f"[Cảnh báo] Lỗi khi đổi mật khẩu trong CSDL: {e}")
            print("=> Chuyển sang kiểm tra/đổi mật khẩu cục bộ (local_accounts.json).")

    # ---- fallback: kiểm tra/đổi mật khẩu trong tài khoản cục bộ ----
    accounts = _load_local_accounts()
    for acc in accounts:
        if acc.get("userId") == user_id:
            if acc.get("password") != old_password:
                return {"success": False, "message": "Mật khẩu hiện tại không đúng. Vui lòng thử lại."}
            acc["password"] = new_password
            _save_local_accounts(accounts)
            return {"success": True,
                    "message": "Đổi mật khẩu thành công! (chế độ cục bộ - chưa nối CSDL)"}

    return {"success": False, "message": "Không tìm thấy tài khoản."}