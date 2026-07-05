"""
membership_ui.py
------------------------------------------------
Giao diện ĐĂNG KÝ THẺ THƯ VIỆN cho ứng dụng Thư Viện Xanh, tách riêng khỏi
file giao diện trang chủ (thu_vien_xanh_app.py), theo đúng cách tổ chức của
auth_ui.py (form Đăng nhập/Đăng ký).

Cách hoạt động:
    - MembershipCardWindow là 1 cửa sổ (Toplevel) hiện lên khi người dùng bấm
      nút "Thẻ thành viên" ở cột trái sau khi đã đăng nhập.
    - Form gồm: Thông tin cá nhân (họ tên, ngày sinh, giới tính, CMND/CCCD,
      địa chỉ, email, số điện thoại), Ảnh chân dung (chọn ảnh từ máy), và
      chọn loại thẻ thư viện (3 loại - đã bỏ "Thẻ gia đình" theo yêu cầu).
    - Bấm "Hủy" -> đóng cửa sổ, quay lại trang chủ (không lưu gì cả).
    - MỖI TÀI KHOẢN CHỈ ĐƯỢC ĐĂNG KÝ THẺ 1 LẦN (kiểm tra qua
      membership_queries.get_membership_card khi mở cửa sổ):
        + Chưa đăng ký -> hiện form trống, bấm "Đăng ký" -> lưu (INSERT/UPDATE
          xuống bảng Reader qua membership_queries.save_membership_card).
        + Đã đăng ký từ trước -> tự nạp sẵn thông tin (kể cả ảnh chân dung)
          lên form ở chế độ xem/chỉnh sửa, bấm "Lưu" -> chỉ UPDATE thông tin
          của thẻ đã có, KHÔNG tạo thêm thẻ mới.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk

from membership_queries import get_membership_card, save_membership_card, persist_avatar

# ----------------------------------------------------------------------------
# MÀU SẮC - dùng chung tông xanh lá với trang chủ (thu_vien_xanh_app.py)
# ----------------------------------------------------------------------------
GREEN = "#2E7D32"
GREEN_DARK = "#1B5E20"
GREEN_LIGHT = "#E8F5E9"
TEXT_DARK = "#222222"
TEXT_GRAY = "#666666"
CARD_BORDER = "#E0E0E0"
RED = "#C62828"

AVATAR_SIZE = (90, 90)

# Các loại thẻ thư viện (đã bỏ "Thẻ gia đình" theo yêu cầu)
CARD_TYPES = [
    {
        "key": "standard",
        "name": "Thẻ thành viên thường",
        "price": "Miễn phí",
        "desc": "Dành cho tất cả bạn đọc.\nĐược mượn tối đa 5 cuốn/lần, thời hạn 14 ngày.",
        "note": None,
    },
    {
        "key": "student",
        "name": "Thẻ học sinh - sinh viên",
        "price": "Miễn phí",
        "desc": "Dành cho học sinh, sinh viên.\nĐược mượn tối đa 7 cuốn/lần, thời hạn 20 ngày.",
        "note": "Cần xuất trình thẻ HS/SV.",
    },
    {
        "key": "lecturer",
        "name": "Thẻ giảng viên",
        "price": "Miễn phí",
        "desc": "Dành cho giảng viên, cán bộ.\nĐược mượn tối đa 10 cuốn/lần, thời hạn 30 ngày.",
        "note": "Cần xuất trình thẻ giảng viên/công tác.",
    },
]


def _make_avatar_placeholder():
    """Vẽ icon người dùng màu xám làm ảnh đại diện mặc định (chưa chọn ảnh)."""
    w, h = AVATAR_SIZE
    img = Image.new("RGB", (w, h), "#F0F0F0")
    draw = ImageDraw.Draw(img)
    # Đầu (hình tròn)
    head_r = int(h * 0.17)
    cx, cy = w / 2, h * 0.36
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill="#BDBDBD")
    # Vai (hình elip cắt ở đáy khung)
    draw.ellipse([w * 0.18, h * 0.55, w * 0.82, h * 1.25], fill="#BDBDBD")
    return ImageTk.PhotoImage(img)


class MembershipCardWindow(tk.Toplevel):
    """Cửa sổ Đăng ký thẻ thư viện.

    master       : cửa sổ cha (trang chủ LibraryApp)
    current_user : dict thông tin người dùng hiện tại (để điền sẵn 1 số trường)
    """

    def __init__(self, master, current_user=None):
        super().__init__(master)
        self.current_user = current_user or {}
        self.selected_image_path = None
        self._avatar_img_ref = None

        # Mỗi tài khoản chỉ được đăng ký thẻ 1 lần: kiểm tra CSDL xem userId
        # này đã có thẻ chưa. Nếu đã có -> chuyển sang chế độ XEM/CHỈNH SỬA
        # (nạp sẵn dữ liệu cũ lên form), thay vì cho đăng ký từ đầu lần nữa.
        user_id = self.current_user.get("userId")
        self.existing_card = get_membership_card(user_id) if user_id else None
        self.is_edit_mode = self.existing_card is not None

        self.title("Thông tin thẻ thư viện" if self.is_edit_mode else "Đăng ký thẻ thư viện")
        self.configure(bg="white")
        self.geometry("1040x760")
        self.minsize(960, 640)
        self.transient(master)

        self._build_scrollable_container()
        self._build_header()
        self._build_body()
        self._build_bottom_buttons()

        self.update_idletasks()
        self._center_on_parent(master)
        self.grab_set()

    # ------------------------------------------------------------------
    def _center_on_parent(self, master):
        try:
            master.update_idletasks()
            mx, my = master.winfo_x(), master.winfo_y()
            mw, mh = master.winfo_width(), master.winfo_height()
            ww, wh = self.winfo_width(), self.winfo_height()
            x = mx + max((mw - ww) // 2, 0)
            y = my + max((mh - wh) // 2, 0)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    # ------------------------------------------------------------------
    def _build_scrollable_container(self):
        outer = tk.Frame(self, bg="white")
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.canvas, bg="white")
        self.content_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.content_window, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ------------------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self.content, bg="white", padx=24, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="📗 THƯ VIỆN XANH", font=("Segoe UI", 13, "bold"),
                  bg="white", fg=GREEN).pack(side="left")

        display_name = self.current_user.get("fullName") or self.current_user.get("username") or ""
        if display_name:
            tk.Label(header, text=f"👤 {display_name}", font=("Segoe UI", 10),
                      bg="white", fg=TEXT_DARK).pack(side="right")

        ttk.Separator(self.content, orient="horizontal").pack(fill="x")

        crumb = tk.Frame(self.content, bg="white", padx=24, pady=10)
        crumb.pack(fill="x")
        home_link = tk.Label(crumb, text="Trang chủ", font=("Segoe UI", 9, "bold"),
                              bg="white", fg=GREEN, cursor="hand2")
        home_link.pack(side="left")
        home_link.bind("<Button-1>", lambda e: self._cancel())
        crumb_text = "   ›   Thông tin thẻ thư viện" if self.is_edit_mode else "   ›   Đăng ký thẻ thư viện"
        tk.Label(crumb, text=crumb_text, font=("Segoe UI", 9),
                  bg="white", fg=TEXT_GRAY).pack(side="left")

    # ------------------------------------------------------------------
    def _build_body(self):
        title_box = tk.Frame(self.content, bg="white", padx=24)
        title_box.pack(fill="x", pady=(4, 16))
        if self.is_edit_mode:
            title_text = "Thông tin thẻ thư viện của bạn"
            desc_text = ("Bạn đã đăng ký thẻ thư viện. Xem lại thông tin bên dưới, chỉnh sửa "
                         "nếu cần rồi bấm \"Lưu\" để cập nhật.")
        else:
            title_text = "Đăng ký thẻ thư viện"
            desc_text = ("Điền đầy đủ thông tin để đăng ký thẻ thư viện và sử dụng "
                         "các dịch vụ tại Thư Viện Xanh.")
        tk.Label(title_box, text=title_text, font=("Segoe UI", 18, "bold"),
                  bg="white", fg=TEXT_DARK).pack(anchor="w")
        tk.Label(title_box, text=desc_text,
                  font=("Segoe UI", 9), bg="white", fg=TEXT_GRAY).pack(anchor="w", pady=(4, 0))

        body = tk.Frame(self.content, bg="white", padx=24)
        body.pack(fill="both", expand=True)

        # ---- Cột trái: form thông tin cá nhân + ảnh chân dung ----
        left_col = tk.Frame(body, bg="white", highlightbackground=CARD_BORDER,
                             highlightthickness=1, padx=22, pady=20)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=(0, 16))
        self._build_personal_form(left_col)

        # ---- Cột phải: chọn loại thẻ thư viện ----
        right_col = tk.Frame(body, bg="white", width=300)
        right_col.pack(side="left", fill="y", pady=(0, 16))
        right_col.pack_propagate(False)
        self._build_card_type_panel(right_col)

    # ------------------------------------------------------------------
    def _prefill(self, card_key, user_key=None):
        """Ưu tiên lấy giá trị đã lưu trong thẻ thành viên (nếu đã đăng ký từ
        trước - chế độ chỉnh sửa), nếu chưa có thì lấy tạm từ current_user."""
        if self.existing_card and self.existing_card.get(card_key):
            return self.existing_card.get(card_key)
        return self.current_user.get(user_key or card_key, "") or ""

    def _build_personal_form(self, parent):
        tk.Label(parent, text="THÔNG TIN CÁ NHÂN", font=("Segoe UI", 11, "bold"),
                  bg="white", fg=TEXT_DARK).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)

        def label(text, row, col, required=True):
            frame = tk.Frame(parent, bg="white")
            frame.grid(row=row, column=col, sticky="w", padx=(0 if col == 0 else 14, 0), pady=(10, 2))
            tk.Label(frame, text=text, font=("Segoe UI", 9), bg="white", fg=TEXT_DARK).pack(side="left")
            if required:
                tk.Label(frame, text=" *", font=("Segoe UI", 9, "bold"), bg="white", fg=RED).pack(side="left")

        def entry(row, col, prefill=""):
            e = tk.Entry(parent, font=("Segoe UI", 10), relief="solid", bd=1)
            e.grid(row=row, column=col, sticky="ew", padx=(0 if col == 0 else 14, 0), ipady=6)
            if prefill:
                e.insert(0, prefill)
            return e

        # Họ và tên / Ngày sinh
        label("Họ và tên", 1, 0)
        label("Ngày sinh", 1, 1)
        self.hoten_entry = entry(2, 0, prefill=self._prefill("fullName"))
        dob_frame = tk.Frame(parent, bg="white")
        dob_frame.grid(row=2, column=1, sticky="ew", padx=(14, 0))
        dob_frame.columnconfigure(0, weight=1)
        self.dob_entry = tk.Entry(dob_frame, font=("Segoe UI", 10), relief="solid", bd=1)
        _dob_prefill = self._prefill("dob")
        if _dob_prefill:
            self.dob_entry.insert(0, _dob_prefill)
            self.dob_entry.config(fg=TEXT_DARK)
        else:
            self.dob_entry.insert(0, "dd/mm/yyyy")
            self.dob_entry.config(fg=TEXT_GRAY)

        def dob_focus_in(_e):
            if self.dob_entry.get() == "dd/mm/yyyy":
                self.dob_entry.delete(0, tk.END)
                self.dob_entry.config(fg=TEXT_DARK)

        def dob_focus_out(_e):
            if not self.dob_entry.get():
                self.dob_entry.config(fg=TEXT_GRAY)
                self.dob_entry.insert(0, "dd/mm/yyyy")

        self.dob_entry.bind("<FocusIn>", dob_focus_in)
        self.dob_entry.bind("<FocusOut>", dob_focus_out)
        self.dob_entry.grid(row=0, column=0, sticky="ew", ipady=6)
        tk.Label(dob_frame, text="📅", bg="white").grid(row=0, column=1, padx=(6, 0))

        # Giới tính / CMND-CCCD
        label("Giới tính", 3, 0)
        label("Số CMND/CCCD", 3, 1)

        self.gender_var = tk.StringVar(value=self._prefill("gender") or "Nam")
        gender_row = tk.Frame(parent, bg="white")
        gender_row.grid(row=4, column=0, sticky="w")
        for text in ("Nam", "Nữ", "Khác"):
            tk.Radiobutton(gender_row, text=text, variable=self.gender_var, value=text,
                            bg="white", font=("Segoe UI", 9), fg=TEXT_DARK,
                            activebackground="white", selectcolor="white").pack(side="left", padx=(0, 10))

        cccd_frame = tk.Frame(parent, bg="white")
        cccd_frame.grid(row=4, column=1, sticky="ew", padx=(14, 0))
        self.cccd_entry = tk.Entry(cccd_frame, font=("Segoe UI", 10), relief="solid", bd=1)
        self.cccd_entry.pack(fill="x", ipady=6)
        _cccd_prefill = self._prefill("cccd")
        if _cccd_prefill:
            self.cccd_entry.insert(0, _cccd_prefill)
        tk.Label(cccd_frame, text="Dùng để xác minh danh tính khi làm thẻ.",
                  font=("Segoe UI", 8), bg="white", fg=TEXT_GRAY).pack(anchor="w", pady=(3, 0))

        # Địa chỉ thường trú (toàn bộ chiều rộng)
        label("Địa chỉ thường trú", 5, 0)
        self.diachi_entry = tk.Entry(parent, font=("Segoe UI", 10), relief="solid", bd=1)
        self.diachi_entry.grid(row=6, column=0, columnspan=2, sticky="ew", ipady=6, pady=(0, 0))
        _diachi_prefill = self._prefill("address")
        if _diachi_prefill:
            self.diachi_entry.insert(0, _diachi_prefill)

        # Email / Số điện thoại
        label("Email", 7, 0)
        label("Số điện thoại", 7, 1)
        self.email_entry = entry(8, 0, prefill=self._prefill("email"))
        self.sdt_entry = entry(8, 1, prefill=self._prefill("phone"))

        # Ảnh chân dung
        tk.Label(parent, text="ẢNH CHÂN DUNG", font=("Segoe UI", 11, "bold"),
                  bg="white", fg=TEXT_DARK).grid(row=9, column=0, columnspan=2, sticky="w", pady=(24, 10))

        photo_row = tk.Frame(parent, bg="white")
        photo_row.grid(row=10, column=0, columnspan=2, sticky="w")

        avatar_frame = tk.Frame(photo_row, bg="white", highlightbackground=CARD_BORDER,
                                 highlightthickness=1)
        avatar_frame.pack(side="left")
        self._placeholder_avatar = _make_avatar_placeholder()
        self.avatar_label = tk.Label(avatar_frame, image=self._placeholder_avatar, bg="white")
        self.avatar_label.image = self._placeholder_avatar
        self.avatar_label.pack()

        # Nếu đã đăng ký thẻ từ trước và có ảnh chân dung đã lưu -> hiển thị lại.
        saved_avatar = self.existing_card.get("avatarPath") if self.existing_card else None
        if saved_avatar and os.path.exists(saved_avatar):
            self._load_avatar_preview(saved_avatar)

        photo_info = tk.Frame(photo_row, bg="white")
        photo_info.pack(side="left", padx=16, fill="y")
        tk.Button(photo_info, text="⭱  Chọn ảnh", bg="white", fg=GREEN,
                  highlightbackground=GREEN, highlightthickness=1, relief="flat",
                  font=("Segoe UI", 9, "bold"), padx=14, pady=6, cursor="hand2",
                  command=self._choose_image).pack(anchor="w")
        for note in ("• Ảnh 3x4, nền sáng, rõ mặt.", "• Dung lượng tối đa 5MB.", "• Định dạng: JPG, PNG."):
            tk.Label(photo_info, text=note, font=("Segoe UI", 8), bg="white",
                      fg=TEXT_GRAY, justify="left").pack(anchor="w", pady=(4, 0))

    # ------------------------------------------------------------------
    def _choose_image(self):
        path = filedialog.askopenfilename(
            title="Chọn ảnh chân dung",
            filetypes=[("Ảnh (JPG, PNG)", "*.jpg *.jpeg *.png"), ("Tất cả file", "*.*")],
        )
        if not path:
            return
        if not self._load_avatar_preview(path):
            messagebox.showerror("Lỗi", "Không thể mở file ảnh này. Vui lòng chọn ảnh khác.", parent=self)
            return
        self.selected_image_path = path

    def _load_avatar_preview(self, path):
        """Hiển thị ảnh tại 'path' lên khung avatar. Trả về True nếu thành công."""
        try:
            img = Image.open(path).convert("RGB")
            # Cắt ảnh thành hình vuông chính giữa rồi resize cho vừa khung avatar.
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side)).resize(AVATAR_SIZE, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=photo)
            self.avatar_label.image = photo
            self._avatar_img_ref = photo
            self.selected_image_path = path
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    def _build_card_type_panel(self, parent):
        tk.Label(parent, text="CHỌN LOẠI THẺ THƯ VIỆN", font=("Segoe UI", 11, "bold"),
                  bg="white", fg=TEXT_DARK).pack(anchor="w", pady=(0, 12))

        default_card_key = (self.existing_card.get("cardType") if self.existing_card else None) or CARD_TYPES[0]["key"]
        self.card_var = tk.StringVar(value=default_card_key)
        self.card_frames = {}

        for card in CARD_TYPES:
            frame = tk.Frame(parent, bg="white", highlightthickness=2, padx=12, pady=10)
            frame.pack(fill="x", pady=(0, 12))
            self.card_frames[card["key"]] = frame

            top_row = tk.Frame(frame, bg="white")
            top_row.pack(fill="x")
            tk.Radiobutton(top_row, text=card["name"], variable=self.card_var, value=card["key"],
                            font=("Segoe UI", 10, "bold"), bg="white", fg=TEXT_DARK,
                            activebackground="white", selectcolor="white",
                            command=self._refresh_card_borders).pack(side="left")
            tk.Label(top_row, text=card["price"], font=("Segoe UI", 9, "bold"),
                      bg="white", fg=GREEN).pack(side="right")

            tk.Label(frame, text=card["desc"], font=("Segoe UI", 9), bg="white",
                      fg=TEXT_GRAY, justify="left", anchor="w").pack(fill="x", padx=(24, 0), pady=(4, 0))

            if card["note"]:
                tk.Label(frame, text=card["note"], font=("Segoe UI", 8, "bold"), bg="white",
                          fg=RED, justify="left", anchor="w").pack(fill="x", padx=(24, 0), pady=(4, 0))

        self._refresh_card_borders()

    def _refresh_card_borders(self):
        selected = self.card_var.get()
        for key, frame in self.card_frames.items():
            if key == selected:
                frame.config(highlightbackground=GREEN, highlightcolor=GREEN)
            else:
                frame.config(highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER)

    # ------------------------------------------------------------------
    def _build_bottom_buttons(self):
        bar = tk.Frame(self.content, bg="white", padx=24, pady=6)
        bar.pack(fill="x")

        btn_row = tk.Frame(bar, bg="white")
        btn_row.pack()

        tk.Button(btn_row, text="Hủy", bg="white", fg=TEXT_DARK,
                  highlightbackground=CARD_BORDER, highlightthickness=1, relief="flat",
                  font=("Segoe UI", 10), padx=30, pady=8, cursor="hand2",
                  command=self._cancel).pack(side="left", padx=(0, 12))

        submit_text = "💾 Lưu" if self.is_edit_mode else "Đăng ký  →"
        tk.Button(btn_row, text=submit_text, bg=GREEN, fg="white",
                  activebackground=GREEN_DARK, activeforeground="white", relief="flat", bd=0,
                  font=("Segoe UI", 10, "bold"), padx=30, pady=8, cursor="hand2",
                  command=self._submit).pack(side="left")

        self._build_footer_features()

    def _build_footer_features(self):
        footer = tk.Frame(self.content, bg=GREEN_LIGHT, padx=20, pady=16)
        footer.pack(fill="x", pady=(20, 0))
        features = [
            ("📚", "Kho sách phong phú", "Đa dạng thể loại"),
            ("🔍", "Mượn sách dễ dàng", "Nhanh chóng, tiện lợi"),
            ("🕒", "Đọc mọi lúc, mọi nơi", "Trên mọi thiết bị"),
            ("🛡️", "An toàn & Bảo mật", "Bảo vệ thông tin"),
        ]
        for icon, title, subtitle in features:
            col = tk.Frame(footer, bg=GREEN_LIGHT)
            col.pack(side="left", expand=True, fill="x")
            tk.Label(col, text=icon, font=("Segoe UI", 18), bg=GREEN_LIGHT).pack()
            tk.Label(col, text=title, font=("Segoe UI", 9, "bold"),
                      bg=GREEN_LIGHT, fg=TEXT_DARK).pack(pady=(4, 0))
            tk.Label(col, text=subtitle, font=("Segoe UI", 8),
                      bg=GREEN_LIGHT, fg=TEXT_GRAY).pack()

    # ------------------------------------------------------------------
    def _cancel(self):
        """Hủy đăng ký -> đóng cửa sổ, quay lại trang chủ (không lưu gì)."""
        self.destroy()

    def _submit(self):
        """Kiểm tra thông tin, nếu hợp lệ -> lưu (đăng ký lần đầu hoặc cập
        nhật nếu đã đăng ký từ trước) vào cơ sở dữ liệu."""
        user_id = self.current_user.get("userId")
        if not user_id:
            messagebox.showerror("Lỗi", "Không xác định được tài khoản. Vui lòng đăng nhập lại.", parent=self)
            return

        required_values = {
            "Họ và tên": self.hoten_entry.get().strip(),
            "Ngày sinh": "" if self.dob_entry.get().strip() == "dd/mm/yyyy" else self.dob_entry.get().strip(),
            "Số CMND/CCCD": self.cccd_entry.get().strip(),
            "Địa chỉ thường trú": self.diachi_entry.get().strip(),
            "Email": self.email_entry.get().strip(),
            "Số điện thoại": self.sdt_entry.get().strip(),
        }

        missing = [name for name, value in required_values.items() if not value]
        if missing:
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập đầy đủ các trường bắt buộc:\n- " + "\n- ".join(missing),
                parent=self,
            )
            return

        # Ảnh chân dung: bắt buộc nếu đăng ký lần đầu; nếu đang chỉnh sửa và
        # trước đó đã có ảnh thì không bắt chọn lại (đã có self.selected_image_path
        # được nạp sẵn từ ảnh cũ).
        if not self.selected_image_path:
            messagebox.showwarning("Thiếu ảnh chân dung",
                                    "Vui lòng chọn ảnh chân dung trước khi tiếp tục.", parent=self)
            return

        previous_avatar = self.existing_card.get("avatarPath") if self.existing_card else None
        avatar_path_to_save = persist_avatar(user_id, self.selected_image_path, previous_avatar)

        data = {
            "fullName": required_values["Họ và tên"],
            "dob": required_values["Ngày sinh"],
            "gender": self.gender_var.get(),
            "cccd": required_values["Số CMND/CCCD"],
            "address": required_values["Địa chỉ thường trú"],
            "email": required_values["Email"],
            "phone": required_values["Số điện thoại"],
            "avatarPath": avatar_path_to_save,
            "cardType": self.card_var.get(),
        }

        result = save_membership_card(user_id, data)
        if not result.get("success"):
            messagebox.showerror("Không thể lưu", result.get("message", "Đã có lỗi xảy ra."), parent=self)
            return

        if self.is_edit_mode:
            messagebox.showinfo("Đã lưu", result.get("message", "Cập nhật thông tin thẻ thành viên thành công!"),
                                 parent=self)
        else:
            messagebox.showinfo(
                "Đăng ký thẻ thành viên thành công",
                "Chào mừng bạn đến với thế giới sách. Hãy chọn ngay cho mình một "
                "cuốn sách yêu thích để \"khai trương\" chiếc thẻ mới này nhé!",
                parent=self,
            )
        self.destroy()