"""
membership_queries.py
------------------------------------------------
Xử lý ĐĂNG KÝ / CẬP NHẬT THẺ THÀNH VIÊN (bảng Reader) cho ứng dụng Thư Viện
Xanh. Tách riêng theo đúng cách tổ chức của auth_queries.py (đăng nhập/đăng ký
tài khoản) và db_queries.py (lấy danh sách sách).

QUY TẮC BẮT BUỘC: MỖI TÀI KHOẢN (userId) CHỈ ĐƯỢC ĐĂNG KÝ THẺ 1 LẦN.
    - Bảng Reader có "userId UNIQUE" (xem LibraryManagement_mysql.sql) nên ở
      cấp CSDL, 1 userId chỉ có thể có TỐI ĐA 1 dòng Reader.
    - Cột Reader.cardType dùng để phân biệt:
        cardType IS NULL  -> tài khoản CHƯA đăng ký thẻ thành viên.
        cardType NOT NULL -> ĐÃ đăng ký (là 1 trong 'standard'/'student'/'lecturer').
    - get_membership_card(user_id): trả về thông tin thẻ đã đăng ký (None nếu
      chưa đăng ký) để giao diện (membership_ui.py) tự động chuyển sang chế
      độ "Xem/Chỉnh sửa" thay vì cho đăng ký lại từ đầu.
    - save_membership_card(user_id, data): LUÔN UPDATE dòng Reader hiện có
      (được tạo sẵn lúc lập tài khoản ở auth_queries.register_reader, hoặc đã
      có thẻ từ trước) nếu đã tồn tại; chỉ INSERT dòng Reader mới khi userId
      đó thật sự CHƯA có dòng Reader nào (trường hợp hiếm, ví dụ tài khoản
      Admin/Librarian). Nhờ vậy không bao giờ tạo ra 2 dòng/2 thẻ cho cùng 1
      userId -> không thể đăng ký nhiều lần.

Chế độ dự phòng (fallback) khi KHÔNG kết nối được MySQL: lưu vào file JSON
cục bộ "local_membership_cards.json" cạnh file này, theo đúng cơ chế
local_accounts.json của auth_queries.py.
"""

import os
import json
import shutil
import datetime

from db_queries import get_db_connection, MYSQL_AVAILABLE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_CARDS_FILE = os.path.join(BASE_DIR, "local_membership_cards.json")
AVATARS_DIR = os.path.join(BASE_DIR, "avatars")

CARD_TYPES_ALLOWED = ("standard", "student", "lecturer")


# ----------------------------------------------------------------------------
# ẢNH CHÂN DUNG - lưu 1 bản sao cố định theo userId (tránh phụ thuộc file gốc
# trên máy người dùng bị xoá/di chuyển sau khi đăng ký).
# ----------------------------------------------------------------------------
def persist_avatar(user_id, chosen_path, previous_path=None):
    """
    Nếu người dùng vừa chọn 1 ảnh MỚI (chosen_path khác thư mục avatars/) thì
    sao chép ảnh đó vào avatars/{userId}.<ext> và trả về đường dẫn đã lưu.
    Nếu chosen_path rỗng hoặc chính là ảnh đã lưu trước đó -> giữ nguyên
    previous_path (không đổi ảnh).
    """
    if not chosen_path:
        return previous_path or ""

    try:
        if os.path.dirname(os.path.abspath(chosen_path)) == os.path.abspath(AVATARS_DIR):
            return chosen_path  # ảnh đang dùng đã là ảnh đã lưu trước đó, không cần copy lại

        os.makedirs(AVATARS_DIR, exist_ok=True)
        ext = os.path.splitext(chosen_path)[1].lower() or ".jpg"
        dest = os.path.join(AVATARS_DIR, f"{user_id}{ext}")
        shutil.copy(chosen_path, dest)
        return dest
    except Exception as e:
        print(f"[Cảnh báo] Không sao chép được ảnh chân dung: {e}")
        return chosen_path


# ----------------------------------------------------------------------------
# LƯU TRỮ CỤC BỘ (FALLBACK) - dùng khi không kết nối được MySQL
# ----------------------------------------------------------------------------
def _load_local_cards():
    if not os.path.exists(LOCAL_CARDS_FILE):
        return []
    try:
        with open(LOCAL_CARDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_local_cards(cards):
    try:
        with open(LOCAL_CARDS_FILE, "w", encoding="utf-8") as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Cảnh báo] Không lưu được local_membership_cards.json: {e}")


def _next_local_reader_id(cards):
    max_num = 0
    for c in cards:
        rid = c.get("readerId", "")
        if rid and rid.startswith("R") and rid[1:].isdigit():
            max_num = max(max_num, int(rid[1:]))
    return f"R{max_num + 1:03d}"


# ----------------------------------------------------------------------------
# LẤY THÔNG TIN THẺ THÀNH VIÊN ĐÃ ĐĂNG KÝ (nếu có)
# ----------------------------------------------------------------------------
def get_membership_card(user_id):
    """
    Trả về dict thông tin thẻ thành viên đã đăng ký của user_id, hoặc None
    nếu tài khoản này CHƯA đăng ký thẻ (cardType rỗng/NULL).
    dict trả về gồm: readerId, fullName, dob (dd/mm/yyyy), gender, cccd,
    address, email, phone, avatarPath, cardType, registeredDate.
    """
    user_id = (user_id or "").strip()
    if not user_id:
        return None

    if MYSQL_AVAILABLE:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT readerId, fullName, dob, gender, cccd, address, "
                "email, phone, avatarPath, cardType, registeredDate "
                "FROM Reader WHERE userId = %s",
                (user_id,),
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if not row or not row[9]:  # cardType rỗng -> chưa đăng ký thẻ
                return None
            dob_val = row[2]
            return {
                "readerId": row[0],
                "fullName": row[1] or "",
                "dob": dob_val.strftime("%d/%m/%Y") if hasattr(dob_val, "strftime") else (dob_val or ""),
                "gender": row[3] or "",
                "cccd": row[4] or "",
                "address": row[5] or "",
                "email": row[6] or "",
                "phone": row[7] or "",
                "avatarPath": row[8] or "",
                "cardType": row[9],
                "registeredDate": str(row[10]) if row[10] else "",
            }
        except Exception as e:
            print(f"[Cảnh báo] Lỗi khi lấy thẻ thành viên từ CSDL: {e}")
            print("=> Chuyển sang kiểm tra dữ liệu cục bộ (local_membership_cards.json).")

    for c in _load_local_cards():
        if c.get("userId") == user_id and c.get("cardType"):
            return dict(c)
    return None


# ----------------------------------------------------------------------------
# ĐĂNG KÝ / CẬP NHẬT THẺ THÀNH VIÊN (mỗi userId chỉ có tối đa 1 thẻ)
# ----------------------------------------------------------------------------
def save_membership_card(user_id, data):
    """
    Lưu thông tin thẻ thành viên cho user_id.
        - Nếu userId CHƯA có dòng Reader nào              -> INSERT dòng mới.
        - Nếu userId ĐÃ có dòng Reader (kể cả dòng "trống"
          được tạo sẵn lúc lập tài khoản, hoặc đã có thẻ)  -> chỉ UPDATE.
      => Không bao giờ tạo thêm dòng thứ 2 cho cùng 1 userId, tức KHÔNG THỂ
         đăng ký thẻ nhiều lần.

    data: dict gồm fullName, dob ("dd/mm/yyyy"), gender, cccd, address,
          email, phone, avatarPath, cardType ('standard'/'student'/'lecturer').

    Trả về dict: {"success": bool, "message": str}
    """
    user_id = (user_id or "").strip()
    if not user_id:
        return {"success": False, "message": "Không xác định được tài khoản. Vui lòng đăng nhập lại."}

    if data.get("cardType") not in CARD_TYPES_ALLOWED:
        return {"success": False, "message": "Loại thẻ không hợp lệ."}

    dob_sql = None
    if data.get("dob"):
        try:
            dob_sql = datetime.datetime.strptime(data["dob"], "%d/%m/%Y").date().isoformat()
        except ValueError:
            dob_sql = None

    today_iso = datetime.date.today().isoformat()

    if MYSQL_AVAILABLE:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT readerId, cardType FROM Reader WHERE userId = %s", (user_id,))
            row = cursor.fetchone()

            if row is None:
                # Chưa từng có dòng Reader (vd tài khoản Admin/Librarian) -> tạo mới.
                cursor.execute("SELECT readerId FROM Reader")
                max_r = 0
                for (rid,) in cursor.fetchall():
                    if rid and rid.startswith("R") and rid[1:].isdigit():
                        max_r = max(max_r, int(rid[1:]))
                new_reader_id = f"R{max_r + 1:03d}"
                expiry = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()

                cursor.execute(
                    "INSERT INTO Reader (readerId, userId, cardExpiryDate, totalBorrowed, "
                    "fullName, dob, gender, cccd, address, email, phone, avatarPath, "
                    "cardType, registeredDate) "
                    "VALUES (%s, %s, %s, 0, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (new_reader_id, user_id, expiry, data.get("fullName"), dob_sql,
                     data.get("gender"), data.get("cccd"), data.get("address"),
                     data.get("email"), data.get("phone"), data.get("avatarPath"),
                     data.get("cardType"), today_iso),
                )
                conn.commit()
                cursor.close()
                conn.close()
                return {"success": True, "message": "Đăng ký thẻ thành viên thành công!"}

            # Đã có dòng Reader từ trước (trống hoặc đã có thẻ) -> LUÔN UPDATE.
            was_new = not row[1]
            cursor.execute(
                "UPDATE Reader SET fullName=%s, dob=%s, gender=%s, cccd=%s, address=%s, "
                "email=%s, phone=%s, avatarPath=%s, cardType=%s, "
                "registeredDate=COALESCE(registeredDate, %s) "
                "WHERE userId=%s",
                (data.get("fullName"), dob_sql, data.get("gender"), data.get("cccd"),
                 data.get("address"), data.get("email"), data.get("phone"),
                 data.get("avatarPath"), data.get("cardType"), today_iso, user_id),
            )
            conn.commit()
            cursor.close()
            conn.close()
            msg = "Đăng ký thẻ thành viên thành công!" if was_new else "Cập nhật thông tin thẻ thành viên thành công!"
            return {"success": True, "message": msg}

        except Exception as e:
            print(f"[Cảnh báo] Lỗi khi lưu thẻ thành viên vào CSDL: {e}")
            print("=> Chuyển sang lưu cục bộ (local_membership_cards.json).")

    # ---- fallback: lưu cục bộ ----
    cards = _load_local_cards()
    for c in cards:
        if c.get("userId") == user_id:
            was_new = not c.get("cardType")
            c.update({
                "fullName": data.get("fullName"), "dob": data.get("dob"),
                "gender": data.get("gender"), "cccd": data.get("cccd"),
                "address": data.get("address"), "email": data.get("email"),
                "phone": data.get("phone"), "avatarPath": data.get("avatarPath"),
                "cardType": data.get("cardType"),
            })
            c.setdefault("registeredDate", today_iso)
            _save_local_cards(cards)
            msg = ("Đăng ký thẻ thành viên thành công! (chế độ cục bộ - chưa nối CSDL)" if was_new
                   else "Cập nhật thông tin thẻ thành viên thành công! (chế độ cục bộ - chưa nối CSDL)")
            return {"success": True, "message": msg}

    new_card = {
        "readerId": _next_local_reader_id(cards), "userId": user_id,
        "fullName": data.get("fullName"), "dob": data.get("dob"),
        "gender": data.get("gender"), "cccd": data.get("cccd"),
        "address": data.get("address"), "email": data.get("email"),
        "phone": data.get("phone"), "avatarPath": data.get("avatarPath"),
        "cardType": data.get("cardType"), "registeredDate": today_iso,
        "cardExpiryDate": (datetime.date.today() + datetime.timedelta(days=365)).isoformat(),
        "totalBorrowed": 0,
    }
    cards.append(new_card)
    _save_local_cards(cards)
    return {"success": True, "message": "Đăng ký thẻ thành viên thành công! (chế độ cục bộ - chưa nối CSDL)"}