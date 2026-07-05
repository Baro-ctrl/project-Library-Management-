"""
Thư Viện Xanh - Giao diện người dùng (Tkinter)
------------------------------------------------
Ứng dụng giao diện desktop mô phỏng theo bản thiết kế (template) trang web thư viện sách.

Cách thêm hình ảnh của bạn:
    Đặt các file ảnh vào thư mục "images/" cạnh file này, đặt tên đúng như trong
    dict IMAGE_PATHS bên dưới, ví dụ:
        images/logo.png
        images/hero_banner.png (banner1), images/banner2.jpg, images/banner3.jpg
        images/side_1.png, images/side_2.png, images/side_3.png
        images/book_1.png, images/book_2.png, ...
    Nếu không tìm thấy file, chương trình sẽ tự vẽ một khung placeholder màu xám
    để bạn biết vị trí ảnh cần thay.

Yêu cầu thư viện: pillow (pip install pillow), pyodbc (pip install pyodbc) để lấy dữ liệu từ SQL Server.

Kết nối database:
    Toàn bộ phần kết nối & truy vấn CSDL nằm ở file riêng "db_queries.py"
    (cùng thư mục với file này). Nếu cần đổi server/database/tài khoản hoặc
    sửa câu truy vấn, hãy chỉnh trong file db_queries.py.
    Nếu không kết nối được (thiếu pyodbc, sai driver, server tắt, v.v...),
    chương trình tự động dùng dữ liệu mẫu (fallback) để giao diện vẫn chạy.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from PIL import Image, ImageDraw, ImageFont, ImageTk

from db_queries import fetch_books_by_category
from auth_ui import AuthWindow
from auth_queries import change_password
from membership_ui import MembershipCardWindow

# ----------------------------------------------------------------------------
# CẤU HÌNH CHUNG
# ----------------------------------------------------------------------------
APP_TITLE = "Thư Viện Xanh"
BG_COLOR = "#FFFFFF"
GREEN = "#2E7D32"
GREEN_DARK = "#1B5E20"
GREEN_LIGHT = "#E8F5E9"
TEXT_DARK = "#222222"
TEXT_GRAY = "#666666"
CARD_BORDER = "#E0E0E0"

# Kích thước khung nút khu vực tài khoản ở header - lấy khung "Đăng nhập"
# (khi CHƯA đăng nhập) làm chuẩn, để khung tên người dùng (khi ĐÃ đăng nhập)
# có cùng kích thước, không bị to/nhỏ khác nhau giữa 2 trạng thái.
ACCOUNT_BUTTON_WIDTH = 150
ACCOUNT_BUTTON_HEIGHT = 38

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")


def resolve_image_path(filename):
    """Tìm file ảnh ở thư mục images/assets gần nhất, bao gồm cả dự án thư viện ở D:\CNPM\QLTV."""
    name, _ = os.path.splitext(filename)
    candidate_dirs = []

    for base in [
        BASE_DIR,
        os.path.dirname(BASE_DIR),
        os.path.join(os.path.dirname(BASE_DIR), "QLTV"),
        r"D:\CNPM\QLTV",
        r"D:\CNPM\QLTV\assets",
        r"D:\CNPM\QLTV\images",
    ]:
        if base and base not in candidate_dirs:
            candidate_dirs.append(base)

    candidates = []
    for root in candidate_dirs:
        for rel in [
            filename,
            name + ".png",
            name + ".jpg",
            name + ".jpeg",
            os.path.join("images", filename),
            os.path.join("images", name + ".png"),
            os.path.join("images", name + ".jpg"),
            os.path.join("images", name + ".jpeg"),
            os.path.join("assets", filename),
            os.path.join("assets", name + ".png"),
            os.path.join("assets", name + ".jpg"),
            os.path.join("assets", name + ".jpeg"),
        ]:
            path = os.path.join(root, rel)
            if path not in candidates:
                candidates.append(path)

    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]


# Đường dẫn ảnh mong đợi - đổi tên file của bạn cho khớp, hoặc sửa lại đường dẫn.
IMAGE_PATHS = {
    "logo": resolve_image_path("Logo.png"),
    "hero_banner": resolve_image_path("banner1.png"),
    "hero_banner_2": resolve_image_path("banner2.jpg"),
    "hero_banner_3": resolve_image_path("banner3.jpg"),
    "side_1": resolve_image_path("sidebar1.png"),
    "side_2": resolve_image_path("sidebar2.png"),
    "side_3": resolve_image_path("sidebar3.png"),
}

# Kích thước riêng cho từng ảnh nhỏ ở cột trái hero section
SIDEBAR_IMAGE_SIZE = (150, 240)
SIDEBAR3_IMAGE_SIZE = (150, 240)

# ----------------------------------------------------------------------------
# DỮ LIỆU MẪU (FALLBACK) - dùng khi không kết nối được database
# (Phần kết nối & truy vấn CSDL nằm ở file db_queries.py)
# ----------------------------------------------------------------------------
# Dữ liệu mẫu cho khối "TIỂU THUYẾT"
_NOVELS_FALLBACK = [
    {"img": "book_tieuthuyet_1.png", "title": "Hoàng tử bé", "author": "Antoine de Saint-Exupéry", "year": "(1943)"},
    {"img": "book_tieuthuyet_2.png", "title": "Harry Potter", "author": "J.K. Rowling", "year": "(2007)"},
    {"img": "book_tieuthuyet_3.png", "title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "year": "(1954)"},
    {"img": "book_tieuthuyet_4.png", "title": "Gone with the Wind", "author": "Margaret Mitchel", "year": "(1936)"},
]

# Dữ liệu mẫu cho khối "VĂN HỌC"
_LITERATURE_FALLBACK = [
    {"img": "book_vanhoc_1.png", "title": "Chí Phèo", "author": "Nam Cao", "year": "(1941)"},
    {"img": "book_vanhoc_2.png", "title": "Lều Chõng", "author": "Ngô Tất Tố", "year": "(1941)"},
    {"img": "book_vanhoc_3.png", "title": "Đất Rừng Phương Nam", "author": "Đoàn Giỏi", "year": ""},
    {"img": "book_vanhoc_4.png", "title": "Truyện Kiều", "author": "Nguyễn Du", "year": "(1820)"},
    {"img": "book_vanhoc_5.png", "title": "Hoàng tử bé", "author": "Antoine de Saint-Exupéry", "year": "(1943)"},
]

# Dữ liệu mẫu cho khối "TRUYỆN TRANH"
_COMICS_FALLBACK = [
    {"img": "comic_1.png", "title": "Doraemon", "author": "Fujiko F. Fujio", "year": ""},
    {"img": "comic_2.png", "title": "Thám Tử Lừng Danh Conan", "author": "Aoyama Gosho", "year": ""},
    {"img": "comic_3.png", "title": "One Piece", "author": "Eiichiro Oda", "year": ""},
    {"img": "comic_4.png", "title": "Naruto", "author": "Masashi Kishimoto", "year": ""},
    {"img": "comic_5.png", "title": "Thần Đồng Đất Việt", "author": "Lê Linh", "year": ""},
]

# Dữ liệu mẫu cho khối "KINH DỊ" (truyện kinh dị)
_HORROR_FALLBACK = [
    {"img": "horror_1.png", "title": "Ngôi Nhà Ma Ám", "author": "Sưu tầm", "year": ""},
    {"img": "horror_2.png", "title": "Con Búp Bê Cổ", "author": "Sưu tầm", "year": ""},
    {"img": "horror_3.png", "title": "Lời Nguyền Đêm Rằm", "author": "Sưu tầm", "year": ""},
    {"img": "horror_4.png", "title": "Oan Hồn Báo Oán", "author": "Sưu tầm", "year": ""},
    {"img": "horror_5.png", "title": "Bóng Ma Cuối Phố", "author": "Sưu tầm", "year": ""},
]

# ----------------------------------------------------------------------------
# DỮ LIỆU THỰC TẾ - lấy từ database (tự động fallback về dữ liệu mẫu nếu lỗi)
# categoryId theo bảng Category: C001=Tiểu Thuyết, C002=Văn Học, C003=Truyện Tranh, C004=Kinh Dị
# ----------------------------------------------------------------------------
NOVELS = fetch_books_by_category("C001", _NOVELS_FALLBACK)
LITERATURE = fetch_books_by_category("C002", _LITERATURE_FALLBACK)
COMICS = fetch_books_by_category("C003", _COMICS_FALLBACK)
HORROR = fetch_books_by_category("C004", _HORROR_FALLBACK)

# Dữ liệu mẫu cho dải tiện ích ở chân trang
FEATURES = [
    ("📚", "Kho sách phong phú", "Đa dạng thể loại"),
    ("🔍", "Tìm sách dễ dàng", "Nhanh chóng, tiện lợi"),
    ("🕒", "Đọc mọi lúc, mọi nơi", "Trên mọi thiết bị"),
    ("🛡️", "An toàn & Bảo mật", "Bảo vệ thông tin"),
]


# ----------------------------------------------------------------------------
# TIỆN ÍCH ẢNH
# ----------------------------------------------------------------------------
def load_or_placeholder(path, size, label="Ảnh"):
    """Tải ảnh từ 'path' và resize về 'size'. Nếu không có file, vẽ placeholder."""
    w, h = size
    try:
        if path and os.path.exists(path):
            img = Image.open(path).convert("RGB")
            img = img.resize((w, h), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
    except Exception:
        pass

    # Vẽ khung placeholder màu xám kèm chữ mô tả
    img = Image.new("RGB", (w, h), "#EAEAEA")
    draw = ImageDraw.Draw(img)
    draw.rectangle([1, 1, w - 2, h - 2], outline="#BBBBBB", width=2)
    text = label
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, (h - th) / 2), text, fill="#999999", font=font)
    return ImageTk.PhotoImage(img)


# ----------------------------------------------------------------------------
# WIDGET TÁI SỬ DỤNG: THẺ SÁCH
# ----------------------------------------------------------------------------
class BookCard(tk.Frame):
    def __init__(self, parent, book, img_size=(120, 170), get_current_user=None, **kwargs):
        super().__init__(parent, bg="white", highlightbackground=CARD_BORDER,
                          highlightthickness=1, **kwargs)
        # get_current_user: hàm callback trả về thông tin user hiện tại (dict)
        # hoặc None nếu chưa đăng nhập. Dùng để kiểm tra trước khi cho mượn sách.
        self.get_current_user = get_current_user
        self._img_ref = load_or_placeholder(
            os.path.join(IMAGES_DIR, book["img"]), img_size, label=book["title"][:10]
        )

        img_label = tk.Label(self, image=self._img_ref, bg="white")
        img_label.pack(padx=8, pady=(8, 6))

        # height=2 -> luôn dành sẵn đúng 2 dòng cho tên sách, kể cả khi tên
        # ngắn chỉ chiếm 1 dòng (dòng còn lại để trống). Nhờ vậy các khung
        # sách có tên ngắn (vd: "Chí Phèo", "Làng") và tên dài phải xuống
        # 2 dòng (vd: "Dế Mèn Phiêu Lưu Ký") vẫn có cùng chiều cao, nút
        # "Mượn sách" luôn thẳng hàng nhau giữa các khung.
        title = tk.Label(self, text=book["title"], font=("Segoe UI", 10, "bold"),
                          bg="white", fg=TEXT_DARK, wraplength=img_size[0],
                          height=2, justify="center", anchor="n")
        title.pack(padx=8, fill="x")

        sub_text = book["author"]
        if book.get("year"):
            sub_text += f"\n{book['year']}"
        # height=2 -> luôn dành sẵn 2 dòng (tác giả + năm), kể cả khi sách
        # không có năm xuất bản (chỉ có 1 dòng tác giả), để chiều cao đồng nhất.
        sub = tk.Label(self, text=sub_text, font=("Segoe UI", 8), bg="white",
                        fg=TEXT_GRAY, justify="center", height=2, anchor="n")
        sub.pack(padx=8, pady=(2, 8), fill="x")

        btn = tk.Button(self, text="Mượn sách", bg=GREEN, fg="white",
                         activebackground=GREEN_DARK, activeforeground="white",
                         font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                         padx=10, pady=4, cursor="hand2",
                         command=lambda b=book: self.on_borrow(b))
        btn.pack(side="bottom", pady=(0, 10))

    def on_borrow(self, book):
        # Kiểm tra trạng thái đăng nhập trước khi cho mượn sách.
        user = self.get_current_user() if self.get_current_user else None
        if not user:
            messagebox.showinfo(
                "Thông báo",
                "Vui lòng đăng nhập và đăng ký thẻ thành viên thư viện "
                "để thực hiện mượn cuốn sách này."
            )
            return
        print(f"Đã bấm 'Mượn sách' cho: {book['title']}")


# ----------------------------------------------------------------------------
# WIDGET: DÒNG TIÊU ĐỀ KHỐI SÁCH (VD: 📖 TIỂU THUYẾT   <   >)
# ----------------------------------------------------------------------------
class SectionHeader(tk.Frame):
    def __init__(self, parent, icon, title, **kwargs):
        super().__init__(parent, bg=BG_COLOR, **kwargs)
        left = tk.Label(self, text=f"{icon}  {title}", font=("Segoe UI", 13, "bold"),
                         bg=BG_COLOR, fg=TEXT_DARK)
        left.pack(side="left")


class RoundedButton(tk.Canvas):
    """Nút dạng viên thuốc (bo tròn 2 đầu), dùng cho khu vực tài khoản ở header
    (nút 'Đăng nhập' hoặc tên người dùng sau khi đăng nhập), phỏng theo kiểu
    nút bo tròn trong bản thiết kế mẫu."""

    def __init__(self, parent, text, icon="👤", command=None,
                 width=170, height=38, fill="white", border=CARD_BORDER,
                 text_color=None, **kwargs):
        bg = parent["bg"] if isinstance(parent, (tk.Frame, tk.Canvas)) else "white"
        super().__init__(parent, width=width, height=height, bg=bg,
                          highlightthickness=0, **kwargs)
        self.command = command
        r = height / 2
        text_color = text_color or TEXT_DARK

        self.create_arc(0, 0, height, height, start=90, extent=180,
                         fill=fill, outline=border)
        self.create_arc(width - height, 0, width, height, start=270, extent=180,
                         fill=fill, outline=border)
        self.create_rectangle(r, 0, width - r, height, fill=fill, outline=fill)
        self.create_line(r, 0, width - r, 0, fill=border)
        self.create_line(r, height - 1, width - r, height - 1, fill=border)
        self.create_text(width / 2, height / 2, text=f"{icon}  {text}",
                          font=("Segoe UI", 10), fill=text_color)

        self.config(cursor="hand2")
        self.bind("<Button-1>", self._on_click)

    def _on_click(self, _event):
        if self.command:
            self.command()


class NavArrow(tk.Button):
    """Nút mũi tên tròn màu xanh dùng cho carousel / cuộn danh sách sách."""
    def __init__(self, parent, direction="left", command=None, **kwargs):
        text = "‹" if direction == "left" else "›"
        super().__init__(parent, text=text, font=("Segoe UI", 14, "bold"),
                          bg=GREEN, fg="white", activebackground=GREEN_DARK,
                          activeforeground="white", relief="flat", bd=0,
                          width=2, height=1, cursor="hand2", command=command, **kwargs)


# ----------------------------------------------------------------------------
# ỨNG DỤNG CHÍNH
# ----------------------------------------------------------------------------
class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1080x900")
        self.configure(bg=BG_COLOR)
        self.minsize(900, 700)

        self.current_user = None  # None = chưa đăng nhập; dict = đã đăng nhập

        self._build_scrollable_container()
        self._build_header()
        self._build_hero_section()
        self._build_book_section("📖", "TIỂU THUYẾT", NOVELS, sidebar_key="side_3", visible_count=4)
        self._build_book_section("📗", "VĂN HỌC", LITERATURE, visible_count=5)
        self._build_book_section("💬", "TRUYỆN TRANH", COMICS, visible_count=5)
        self._build_book_section("👻", "KINH DỊ", HORROR, visible_count=5)
        self._build_footer_features()

    # ------------------------------------------------------------------
    def _build_scrollable_container(self):
        """Tạo canvas có thanh cuộn dọc để chứa toàn bộ nội dung trang."""
        container = tk.Frame(self, bg=BG_COLOR)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.canvas, bg=BG_COLOR)
        self.content_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/Mac
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))  # Linux
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.content_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self.content, bg="white", padx=20, pady=14)
        header.pack(fill="x")

        # Logo + tên
        logo_frame = tk.Frame(header, bg="white")
        logo_frame.pack(side="left")
        logo_img = load_or_placeholder(IMAGE_PATHS["logo"], (150, 90), label="Logo")
        self._logo_ref = logo_img
        tk.Label(logo_frame, image=logo_img, bg="white").pack(side="left", padx=(0, 8))

        # Ô tìm kiếm ở giữa
        search_frame = tk.Frame(header, bg="#F5F5F5", highlightbackground=CARD_BORDER,
                                 highlightthickness=1)
        search_frame.pack(side="left", expand=True, fill="x", padx=40)
        tk.Label(search_frame, text="🔍", bg="#F5F5F5").pack(side="left", padx=(10, 4))
        search_entry = tk.Entry(search_frame, bg="#F5F5F5", relief="flat",
                                 font=("Segoe UI", 10), fg=TEXT_GRAY)
        search_entry.insert(0, "Tìm kiếm sách, tác giả, thể loại...")
        search_entry.pack(side="left", fill="x", expand=True, ipady=6)
        tk.Button(search_frame, text="Tìm kiếm", bg=GREEN, fg="white",
                  activebackground=GREEN_DARK, activeforeground="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", bd=0,
                  padx=14, pady=6, cursor="hand2").pack(side="right", padx=4, pady=4)

        # Khu vực tài khoản bên phải: hiển thị nút "Đăng nhập" khi chưa đăng
        # nhập, hoặc tên người dùng + vai trò sau khi đăng nhập thành công.
        self.account_area = tk.Frame(header, bg="white")
        self.account_area.pack(side="right")
        self._render_account_area()

        # Thanh điều hướng phụ (Trang chủ)
        nav = tk.Frame(self.content, bg="white", padx=20)
        nav.pack(fill="x")
        tk.Label(nav, text="Trang chủ", font=("Segoe UI", 10, "bold"),
                 bg="white", fg=GREEN).pack(side="left", pady=(0, 10))
        ttk.Separator(self.content, orient="horizontal").pack(fill="x")

    # ------------------------------------------------------------------
    def _fit_account_text(self, text, icon="👤", font=("Segoe UI", 10)):
        """Rút gọn 'text' (thêm '...') nếu quá dài so với ACCOUNT_BUTTON_WIDTH,
        để khung tài khoản luôn giữ đúng kích thước chuẩn (bằng khung
        "Đăng nhập"), không bị vỡ layout khi tên người dùng dài."""
        fnt = tkfont.Font(family=font[0], size=font[1])
        # Trừ hao khoảng đệm 2 đầu viên thuốc + khoảng cách giữa icon và chữ.
        max_text_width = ACCOUNT_BUTTON_WIDTH - fnt.measure(f"{icon}  ") - 24
        if fnt.measure(text) <= max_text_width:
            return text
        trimmed = text
        while trimmed and fnt.measure(trimmed + "...") > max_text_width:
            trimmed = trimmed[:-1]
        return f"{trimmed}..." if trimmed else text[:1]

    def _render_account_area(self):
        """Vẽ lại khu vực tài khoản ở header, dựa theo self.current_user."""
        for widget in self.account_area.winfo_children():
            widget.destroy()

        if self.current_user:
            role_labels = {"Admin": "Quản trị viên", "Librarian": "Thủ thư", "Reader": "Độc giả"}
            role_text = role_labels.get(self.current_user.get("role"), self.current_user.get("role", ""))
            display_text = f"{self.current_user.get('fullName') or self.current_user.get('username')} ({role_text})"
            display_text = self._fit_account_text(display_text)
            RoundedButton(self.account_area, text=display_text, icon="👤",
                          command=self._confirm_logout,
                          width=ACCOUNT_BUTTON_WIDTH, height=ACCOUNT_BUTTON_HEIGHT).pack(side="right")
        else:
            RoundedButton(self.account_area, text="Đăng nhập", icon="👤",
                          command=self.open_auth_window,
                          width=ACCOUNT_BUTTON_WIDTH, height=ACCOUNT_BUTTON_HEIGHT).pack(side="right")

    def open_auth_window(self, start_mode="login"):
        """Mở cửa sổ Đăng nhập / Đăng ký (auth_ui.AuthWindow)."""
        AuthWindow(self, on_success=self._handle_login_success, start_mode=start_mode)

    def _handle_login_success(self, user):
        """Callback khi đăng nhập thành công: cập nhật header hiển thị tên + vai trò,
        đồng thời chuyển cột trái sang 8 nút chức năng tài khoản."""
        self.current_user = user
        self._render_account_area()
        self._render_side_col()

    def _confirm_logout(self):
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất không?"):
            self.current_user = None
            self._render_account_area()
            self._render_side_col()

    # ------------------------------------------------------------------
    def _render_side_col(self):
        """Vẽ lại cột trái của hero section: ảnh minh hoạ (chưa đăng nhập)
        hoặc 8 nút chức năng tài khoản (đã đăng nhập)."""
        for widget in self.side_col.winfo_children():
            widget.destroy()

        if self.current_user:
            self._build_account_menu(self.side_col)
        else:
            self._build_side_images(self.side_col)

    def _build_side_images(self, parent):
        """2 ảnh nhỏ xếp chồng (side_1, side_2) - hiển thị khi chưa đăng nhập."""
        for key in ("side_1", "side_2"):
            img = load_or_placeholder(IMAGE_PATHS[key], SIDEBAR_IMAGE_SIZE, label=key)
            frame = tk.Frame(parent, bg="white", highlightbackground=CARD_BORDER,
                              highlightthickness=1)
            frame.pack(pady=6)
            lbl = tk.Label(frame, image=img, bg="white")
            lbl.image = img  # giữ tham chiếu tránh bị garbage-collect
            lbl.pack()

    def _build_account_menu(self, parent):
        """8 nút chức năng tài khoản - hiển thị khi đã đăng nhập, thay cho side_1/side_2."""
        tk.Label(parent, text="Tài khoản của tôi", font=("Segoe UI", 12, "bold"),
                  bg=BG_COLOR, fg=GREEN, anchor="w", cursor="hand2").pack(
            fill="x", pady=(0, 8), padx=2)

        box1 = tk.Frame(parent, bg="white", highlightbackground=CARD_BORDER,
                         highlightthickness=1)
        box1.pack(fill="x", pady=(0, 12))
        self._fill_menu_box(box1, [
            ("👤", "Thông tin cá nhân", self.open_profile),
            ("🎫", "Thẻ thành viên", self.open_membership_card),
            ("🕒", "Lịch sử mượn", self.open_borrow_history),
            ("🔔", "Thông báo", self.open_notifications),
        ])

        box2 = tk.Frame(parent, bg="white", highlightbackground=CARD_BORDER,
                         highlightthickness=1)
        box2.pack(fill="x")
        self._fill_menu_box(box2, [
            ("👤", "Quản lý tài khoản", self.open_manage_account),
            ("🔑", "Đổi mật khẩu", self.open_change_password),
            ("🚪", "Đăng xuất", self._confirm_logout),
        ])

    def _fill_menu_box(self, box, items):
        """Thêm các dòng nút (icon + chữ) vào 1 khung (box), có gạch phân
        cách giữa các dòng và hiệu ứng đổi màu khi rê chuột (hover)."""
        for i, (icon, text, command) in enumerate(items):
            self._add_menu_row(box, icon, text, command)
            if i < len(items) - 1:
                ttk.Separator(box, orient="horizontal").pack(fill="x")

    def _add_menu_row(self, parent, icon, text, command):
        row = tk.Frame(parent, bg="white", cursor="hand2")
        row.pack(fill="x")
        lbl = tk.Label(row, text=f"{icon}  {text}", font=("Segoe UI", 10),
                        bg="white", fg=TEXT_DARK, anchor="w", cursor="hand2")
        lbl.pack(fill="x", padx=10, pady=9)

        def on_click(_event=None):
            if command:
                command()

        def on_enter(_event=None):
            row.config(bg=GREEN_LIGHT)
            lbl.config(bg=GREEN_LIGHT)

        def on_leave(_event=None):
            row.config(bg="white")
            lbl.config(bg="white")

        for widget in (row, lbl):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    # --- Các hành động của 8 nút chức năng tài khoản (đang phát triển) ---
    def open_profile(self):
        messagebox.showinfo("Thông tin cá nhân", "Chức năng đang được phát triển.")

    def open_membership_card(self):
        MembershipCardWindow(self, current_user=self.current_user)

    def open_borrow_history(self):
        messagebox.showinfo("Lịch sử mượn", "Chức năng đang được phát triển.")

    def open_notifications(self):
        messagebox.showinfo("Thông báo", "Chức năng đang được phát triển.")

    def open_manage_account(self):
        messagebox.showinfo("Quản lý tài khoản", "Chức năng đang được phát triển.")

    def open_change_password(self):
        """Mở cửa sổ Đổi mật khẩu: yêu cầu mật khẩu hiện tại + mật khẩu mới,
        kiểm tra và cập nhật qua auth_queries.change_password()."""
        if not self.current_user:
            return

        win = tk.Toplevel(self)
        win.title("Đổi mật khẩu")
        win.configure(bg="white")
        win.resizable(False, False)
        win.transient(self)

        container = tk.Frame(win, bg="white", padx=30, pady=24)
        container.pack()

        tk.Label(container, text="Đổi mật khẩu", font=("Segoe UI", 14, "bold"),
                  bg="white", fg=TEXT_DARK).pack(pady=(0, 18))

        def add_field(label_text, show="*"):
            tk.Label(container, text=label_text, font=("Segoe UI", 9),
                      bg="white", fg=TEXT_GRAY, anchor="w").pack(fill="x")
            entry = tk.Entry(container, font=("Segoe UI", 10), show=show,
                              relief="solid", bd=1, width=30)
            entry.pack(pady=(2, 12), ipady=6)
            return entry

        old_entry = add_field("Mật khẩu hiện tại")
        new_entry = add_field("Mật khẩu mới")
        confirm_entry = add_field("Xác nhận mật khẩu mới")

        def submit():
            old_pw = old_entry.get().strip()
            new_pw = new_entry.get().strip()
            confirm_pw = confirm_entry.get().strip()

            if not old_pw or not new_pw or not confirm_pw:
                messagebox.showwarning("Thiếu thông tin",
                                        "Vui lòng nhập đầy đủ thông tin.", parent=win)
                return
            if new_pw != confirm_pw:
                messagebox.showerror("Lỗi",
                                      "Mật khẩu mới và xác nhận mật khẩu không khớp.", parent=win)
                return
            if len(new_pw) < 4:
                messagebox.showwarning("Mật khẩu quá ngắn",
                                        "Mật khẩu mới nên có ít nhất 4 ký tự.", parent=win)
                return

            result = change_password(self.current_user.get("userId"), old_pw, new_pw)
            if result["success"]:
                messagebox.showinfo("Thành công", result["message"], parent=win)
                win.destroy()
            else:
                messagebox.showerror("Đổi mật khẩu thất bại", result["message"], parent=win)

        tk.Button(container, text="Xác nhận", bg=GREEN, fg="white",
                  activebackground=GREEN_DARK, activeforeground="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                  width=24, pady=8, cursor="hand2", command=submit).pack(pady=(6, 6))

        tk.Button(container, text="Hủy", bg="white", fg=TEXT_GRAY,
                  relief="flat", bd=0, font=("Segoe UI", 9),
                  cursor="hand2", command=win.destroy).pack()

        win.bind("<Return>", lambda e: submit())

        win.update_idletasks()
        try:
            self.update_idletasks()
            mx, my = self.winfo_x(), self.winfo_y()
            mw, mh = self.winfo_width(), self.winfo_height()
            ww, wh = win.winfo_width(), win.winfo_height()
            x = mx + (mw - ww) // 2
            y = my + (mh - wh) // 2
            win.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        except Exception:
            pass

        win.grab_set()
        old_entry.focus_set()

    # ------------------------------------------------------------------
    def _build_hero_section(self):
        wrapper = tk.Frame(self.content, bg=BG_COLOR, padx=20, pady=16)
        wrapper.pack(fill="x")

        # Cột trái: khi CHƯA đăng nhập -> 2 ảnh nhỏ xếp chồng (side_1, side_2).
        # Khi ĐÃ đăng nhập -> 8 nút chức năng tài khoản (xem _render_side_col).
        self.side_col = tk.Frame(wrapper, bg=BG_COLOR, width=190)
        self.side_col.pack(side="left", fill="y", padx=(0, 16))
        self.side_col.pack_propagate(False)
        self._render_side_col()

        # Cột phải: banner lớn dạng carousel (banner1 -> banner2 -> banner3 -> xoay vòng)
        hero_frame = tk.Frame(wrapper, bg="white", highlightbackground=CARD_BORDER,
                               highlightthickness=1)
        hero_frame.pack(side="left", fill="both", expand=True)

        hero_inner = tk.Frame(hero_frame, bg="#FDF6EC")
        hero_inner.pack(fill="both", expand=True, padx=2, pady=2)

        # Danh sách các banner theo thứ tự hiển thị trong carousel
        hero_keys = ["hero_banner", "hero_banner_2", "hero_banner_3"]
        hero_size = (710, 540)
        hero_imgs_cache = {}  # nạp ảnh 1 lần rồi tái sử dụng, tránh load lại mỗi lần bấm

        def get_hero_image(key):
            if key not in hero_imgs_cache:
                hero_imgs_cache[key] = load_or_placeholder(
                    IMAGE_PATHS[key], hero_size, label="Banner chính (carousel)"
                )
            return hero_imgs_cache[key]

        state = {"index": 0}

        hero_label = tk.Label(hero_inner, image=get_hero_image(hero_keys[0]), bg="#FDF6EC")
        hero_label.image = get_hero_image(hero_keys[0])  # giữ tham chiếu tránh bị garbage-collect
        hero_label.pack(side="left", fill="both", expand=True)

        def render_hero():
            img = get_hero_image(hero_keys[state["index"]])
            hero_label.config(image=img)
            hero_label.image = img  # giữ tham chiếu tránh bị garbage-collect

        def go_prev():
            """Bấm 1 lần -> lùi về banner trước đó, xoay vòng về banner cuối."""
            state["index"] = (state["index"] - 1) % len(hero_keys)
            render_hero()

        def go_next():
            """Bấm 1 lần -> chuyển sang banner kế tiếp, xoay vòng về banner đầu."""
            state["index"] = (state["index"] + 1) % len(hero_keys)
            render_hero()

        # Mũi tên trái/phải nổi trên banner
        NavArrow(hero_frame, "left", command=go_prev).place(relx=0.02, rely=0.5, anchor="w")
        NavArrow(hero_frame, "right", command=go_next).place(relx=0.98, rely=0.5, anchor="e")

    # ------------------------------------------------------------------
    def _build_book_section(self, icon, title, books, sidebar_key=None, visible_count=4):
        """sidebar_key: nếu được truyền (vd 'side_3'), một ảnh nhỏ sẽ được đặt
        ở bên trái, ngang hàng (cùng chiều cao) với tiêu đề + hàng thẻ sách của khối này.

        visible_count: số khung sách hiển thị cùng lúc (TIỂU THUYẾT = 4, còn
        VĂN HỌC/TRUYỆN TRANH/KINH DỊ = 5). Mỗi lần bấm nút mũi tên (NavArrow)
        chỉ TRƯỢT đi 1 khung: bớt 1 khung ở đầu và thêm 1 khung mới ở cuối
        (nút phải) hoặc ngược lại (nút trái), xoay vòng qua toàn bộ danh sách
        'books' của khối (NOVELS/LITERATURE/COMICS/HORROR)."""
        section = tk.Frame(self.content, bg=BG_COLOR, padx=20, pady=14)
        section.pack(fill="x")

        outer = tk.Frame(section, bg=BG_COLOR)
        outer.pack(fill="x")

        if sidebar_key:
            size = SIDEBAR3_IMAGE_SIZE if sidebar_key == "side_3" else SIDEBAR_IMAGE_SIZE
            side_img = load_or_placeholder(IMAGE_PATHS[sidebar_key], size, label=sidebar_key)
            side_frame = tk.Frame(outer, bg="white", highlightbackground=CARD_BORDER,
                                   highlightthickness=1)
            side_frame.pack(side="left", padx=(0, 16), anchor="n")
            side_lbl = tk.Label(side_frame, image=side_img, bg="white")
            side_lbl.image = side_img  # giữ tham chiếu tránh bị garbage-collect
            side_lbl.pack()
            main_col = tk.Frame(outer, bg=BG_COLOR)
            main_col.pack(side="left", fill="both", expand=True)
        else:
            main_col = outer

        SectionHeader(main_col, icon, title).pack(fill="x", pady=(0, 10))

        row = tk.Frame(main_col, bg=BG_COLOR)
        row.pack(fill="x")

        cards_frame = tk.Frame(row, bg=BG_COLOR)

        # --- Trạng thái trượt (sliding window) cho khối này (mỗi khối riêng) ---
        total_books = len(books)
        # Không cho trượt nếu số sách <= số khung hiển thị (không có gì để thay)
        can_slide = total_books > visible_count
        state = {"start": 0}  # chỉ số (index) của khung đầu tiên đang hiển thị

        def render_page():
            """Vẽ lại đúng dải 'visible_count' khung sách bắt đầu từ state['start']."""
            # Ghi lại vị trí cuộn hiện tại của TOÀN trang trước khi xoá thẻ sách cũ.
            # Lý do: khi xoá hết thẻ cũ, khung chứa khối này tạm thời co về chiều
            # cao 0 trước khi thẻ mới được vẽ lại, khiến scrollregion của canvas
            # co lại tạm thời. Nếu khối này nằm ở cuối trang (vd: KINH DỊ, ngay
            # trước phần chân trang rất ngắn) thì vị trí cuộn hiện tại (đang xem
            # gần cuối trang) sẽ vượt quá giới hạn cuộn mới, khiến Tkinter tự
            # động kẹp (clamp) thanh cuộn lên khối phía trên (vd: TRUYỆN TRANH)
            # -> gây cảm giác giao diện bị "nhảy". Ta khôi phục lại vị trí cuộn
            # ngay sau khi vẽ xong thẻ mới để tránh hiện tượng này.
            scroll_top = self.canvas.yview()[0]

            for widget in cards_frame.winfo_children():
                widget.destroy()

            if total_books == 0:
                return

            start = state["start"]
            visible_books = [
                books[(start + i) % total_books] for i in range(min(visible_count, total_books))
            ]

            for book in visible_books:
                card = BookCard(cards_frame, book, get_current_user=lambda: self.current_user)
                card.pack(side="left", padx=8, pady=4)

            arrow_state = tk.NORMAL if can_slide else tk.DISABLED
            left_arrow.config(state=arrow_state)
            right_arrow.config(state=arrow_state)

            # Khôi phục lại vị trí cuộn như trước khi vẽ lại, tránh giao diện bị nhảy.
            self.canvas.update_idletasks()
            self.canvas.yview_moveto(scroll_top)

        def go_prev():
            """Bấm 1 lần -> bớt 1 khung ở cuối, thêm lại 1 khung mới (khung trước đó) ở đầu."""
            if not can_slide:
                return
            state["start"] = (state["start"] - 1) % total_books
            render_page()

        def go_next():
            """Bấm 1 lần -> bớt 1 khung ở đầu, thêm 1 khung mới ở cuối."""
            if not can_slide:
                return
            state["start"] = (state["start"] + 1) % total_books
            render_page()

        left_arrow = NavArrow(row, "left", command=go_prev)
        left_arrow.pack(side="left", padx=(0, 8))

        cards_frame.pack(side="left", fill="x", expand=True)

        right_arrow = NavArrow(row, "right", command=go_next)
        right_arrow.pack(side="left", padx=(8, 0))

        render_page()  # Vẽ khung sách đầu tiên khi khởi tạo

        ttk.Separator(self.content, orient="horizontal").pack(fill="x", pady=(10, 0))

    # ------------------------------------------------------------------
    def _build_footer_features(self):
        footer = tk.Frame(self.content, bg=GREEN_LIGHT, padx=20, pady=18)
        footer.pack(fill="x")

        for icon, title, subtitle in FEATURES:
            col = tk.Frame(footer, bg=GREEN_LIGHT)
            col.pack(side="left", expand=True, fill="x")
            tk.Label(col, text=icon, font=("Segoe UI", 20), bg=GREEN_LIGHT).pack()
            tk.Label(col, text=title, font=("Segoe UI", 10, "bold"),
                     bg=GREEN_LIGHT, fg=TEXT_DARK).pack(pady=(4, 0))
            tk.Label(col, text=subtitle, font=("Segoe UI", 9),
                     bg=GREEN_LIGHT, fg=TEXT_GRAY).pack()


# ----------------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(IMAGES_DIR, exist_ok=True)  # tạo sẵn thư mục images/ nếu chưa có
    app = LibraryApp()
    app.mainloop()