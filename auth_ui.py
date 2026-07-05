"""
auth_ui.py
------------------------------------------------
Giao diện ĐĂNG NHẬP / ĐĂNG KÝ cho ứng dụng Thư Viện Xanh, tách riêng khỏi
file giao diện trang chủ (thu_vien_xanh_app.py) để dễ bảo trì và có thể tái
sử dụng cho các cửa sổ khác nếu cần.

Cách hoạt động:
    - AuthWindow là 1 cửa sổ (Toplevel) hiện lên khi người dùng bấm nút
      "Đăng nhập" ở trang chủ.
    - Cửa sổ có 2 form dùng chung 1 khung: form Đăng nhập và form Đăng ký,
      chuyển qua lại bằng link chữ xanh (giống bản thiết kế mẫu).
    - Khi đăng ký thành công -> tự động quay về form Đăng nhập (đã điền sẵn
      email/số điện thoại vừa đăng ký) để người dùng đăng nhập ngay.
    - Khi đăng nhập thành công -> gọi callback on_success(user) rồi đóng
      cửa sổ; trang chủ (thu_vien_xanh_app.py) sẽ dùng callback này để cập
      nhật nút đăng nhập thành tên người dùng + vai trò.

Phần truy vấn/ghi CSDL nằm ở file riêng "auth_queries.py".
"""

import tkinter as tk
from tkinter import messagebox

from auth_queries import login_user, register_reader

# ----------------------------------------------------------------------------
# MÀU SẮC - dùng chung tông xanh lá với trang chủ (thu_vien_xanh_app.py)
# ----------------------------------------------------------------------------
GREEN = "#2E7D32"
GREEN_DARK = "#1B5E20"
GREEN_LIGHT = "#E8F5E9"
TEXT_DARK = "#222222"
TEXT_GRAY = "#666666"

WINDOW_SIZE = (480, 620)


class AuthWindow(tk.Toplevel):
    """Cửa sổ Đăng nhập / Đăng ký (dùng chung 1 cửa sổ, chuyển đổi giữa 2 form).

    master     : cửa sổ cha (trang chủ LibraryApp)
    on_success : callback(user_dict) được gọi khi ĐĂNG NHẬP thành công
    start_mode : "login" hoặc "register" - form hiển thị đầu tiên
    """

    def __init__(self, master, on_success=None, start_mode="login"):
        super().__init__(master)
        self.on_success = on_success
        self.title("Thư Viện Xanh")
        self.resizable(False, False)
        w, h = WINDOW_SIZE
        self.configure(bg="white")
        self.transient(master)

        self.canvas = tk.Canvas(self, width=w, height=h, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self._draw_decoration(w, h)

        self.form_container = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window(w // 2, h // 2, window=self.form_container)

        if start_mode == "register":
            self._build_register_form()
        else:
            self._build_login_form()

        self.update_idletasks()
        self._center_on_parent(master)
        self.grab_set()

    # ------------------------------------------------------------------
    def _center_on_parent(self, master):
        """Canh cửa sổ đăng nhập/đăng ký ra giữa cửa sổ trang chủ."""
        w, h = WINDOW_SIZE
        try:
            master.update_idletasks()
            mx, my = master.winfo_x(), master.winfo_y()
            mw, mh = master.winfo_width(), master.winfo_height()
            x = mx + (mw - w) // 2
            y = my + (mh - h) // 2
        except Exception:
            x, y = 200, 100
        self.geometry(f"{w}x{h}+{max(x, 0)}+{max(y, 0)}")

    # ------------------------------------------------------------------
    def _draw_decoration(self, w, h):
        """Vẽ các khối tròn màu xanh trang trí ở góc, phỏng theo bản thiết kế mẫu."""
        c = self.canvas
        # Vòng tròn lớn góc trên-trái (tràn ra ngoài khung)
        c.create_oval(-140, -140, 160, 160, fill=GREEN, outline="")
        c.create_oval(-70, -70, 90, 90, fill=GREEN_DARK, outline="")
        # Vòng tròn lớn góc dưới-phải
        c.create_oval(w - 160, h - 160, w + 140, h + 140, fill=GREEN, outline="")
        c.create_oval(w - 90, h - 90, w + 70, h + 70, fill=GREEN_DARK, outline="")
        # Vài chấm tròn nhỏ trang trí rải rác, giống ảnh mẫu
        for (x, y, r) in [(w - 36, 28, 9), (28, h - 36, 7), (w * 0.8, h * 0.1, 5),
                          (w * 0.12, h * 0.86, 6)]:
            c.create_oval(x - r, y - r, x + r, y + r, fill=GREEN_LIGHT, outline=GREEN)

    # ------------------------------------------------------------------
    def _clear_form(self):
        for widget in self.form_container.winfo_children():
            widget.destroy()

    def _build_header_texts(self, subtitle, switch_text, switch_link_text, switch_command):
        tk.Label(self.form_container, text="CHÀO MỪNG BẠN ĐẾN VỚI",
                 font=("Segoe UI", 12, "bold"), bg="white", fg=TEXT_DARK).pack(pady=(6, 0))
        tk.Label(self.form_container, text="THƯ VIỆN XANH",
                 font=("Segoe UI", 12, "bold"), bg="white", fg=TEXT_DARK).pack()

        tk.Label(self.form_container, text=subtitle, font=("Segoe UI", 16, "bold"),
                 bg="white", fg=TEXT_DARK).pack(pady=(18, 4))

        switch_row = tk.Frame(self.form_container, bg="white")
        switch_row.pack(pady=(0, 16))
        tk.Label(switch_row, text=switch_text, font=("Segoe UI", 9),
                 bg="white", fg=TEXT_GRAY).pack(side="left")
        link = tk.Label(switch_row, text=switch_link_text, font=("Segoe UI", 9, "bold"),
                         bg="white", fg=GREEN, cursor="hand2")
        link.pack(side="left", padx=(4, 0))
        link.bind("<Button-1>", lambda e: switch_command())

    def _make_entry(self, placeholder, show=None):
        """Tạo 1 ô nhập liệu có chữ mờ gợi ý (placeholder), tự ẩn khi bấm vào."""
        entry = tk.Entry(self.form_container, font=("Segoe UI", 10), fg=TEXT_GRAY,
                          relief="solid", bd=1, width=34, justify="left")
        entry.insert(0, placeholder)

        def on_focus_in(_event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=TEXT_DARK)
                if show:
                    entry.config(show=show)

        def on_focus_out(_event):
            if not entry.get():
                entry.config(fg=TEXT_GRAY, show="")
                entry.insert(0, placeholder)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.pack(pady=6, ipady=7, ipadx=6)
        return entry

    def _get_value(self, entry, placeholder):
        val = entry.get().strip()
        return "" if val == placeholder else val

    def _build_social_row(self):
        social = tk.Frame(self.form_container, bg="white")
        social.pack(pady=(8, 0))
        for icon in ("📘", "📷", "🔎"):
            tk.Label(social, text=icon, font=("Segoe UI", 13), bg="white",
                     fg=TEXT_DARK).pack(side="left", padx=8)

    # ------------------------------------------------------------------
    # FORM ĐĂNG NHẬP
    # ------------------------------------------------------------------
    def _build_login_form(self):
        self._clear_form()
        self.mode = "login"

        self._build_header_texts(
            subtitle="Đăng nhập",
            switch_text="Bạn chưa có tài khoản?",
            switch_link_text="Đăng ký",
            switch_command=self._build_register_form,
        )

        self.login_identifier = self._make_entry("Nhập số điện thoại / email")
        self.login_password = self._make_entry("Nhập mật khẩu", show="*")

        forgot = tk.Label(self.form_container, text="Quên mật khẩu?", font=("Segoe UI", 9, "bold"),
                           bg="white", fg=GREEN, cursor="hand2")
        forgot.pack(anchor="w", pady=(2, 16))
        forgot.bind("<Button-1>", lambda e: messagebox.showinfo(
            "Quên mật khẩu", "Vui lòng liên hệ thủ thư để được hỗ trợ đặt lại mật khẩu."))

        tk.Button(self.form_container, text="Đăng nhập", bg=GREEN, fg="white",
                  activebackground=GREEN_DARK, activeforeground="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                  width=28, pady=9, cursor="hand2",
                  command=self._do_login).pack(pady=(0, 6))

        self._build_social_row()

        self.bind("<Return>", lambda e: self._do_login())

    def _do_login(self):
        identifier = self._get_value(self.login_identifier, "Nhập số điện thoại / email")
        password = self._get_value(self.login_password, "Nhập mật khẩu")
        if not identifier or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin đăng nhập.")
            return

        user = login_user(identifier, password)
        if user:
            if self.on_success:
                self.on_success(user)
            self.destroy()
        else:
            messagebox.showerror("Đăng nhập thất bại",
                                  "Sai thông tin đăng nhập hoặc mật khẩu. Vui lòng thử lại.")

    # ------------------------------------------------------------------
    # FORM ĐĂNG KÝ
    # ------------------------------------------------------------------
    def _build_register_form(self):
        self._clear_form()
        self.mode = "register"

        self._build_header_texts(
            subtitle="Tạo Tài Khoản",
            switch_text="Đã có tài khoản?",
            switch_link_text="Đăng nhập",
            switch_command=self._build_login_form,
        )

        self.reg_username = self._make_entry("Nhập tên người dùng")
        self.reg_contact = self._make_entry("Nhập Email/ Số điện thoại")
        self.reg_password = self._make_entry("Nhập mật khẩu", show="*")

        tk.Button(self.form_container, text="Đăng ký", bg=GREEN, fg="white",
                  activebackground=GREEN_DARK, activeforeground="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                  width=28, pady=9, cursor="hand2",
                  command=self._do_register).pack(pady=(16, 6))

        self._build_social_row()

        self.bind("<Return>", lambda e: self._do_register())

    def _do_register(self):
        username = self._get_value(self.reg_username, "Nhập tên người dùng")
        contact = self._get_value(self.reg_contact, "Nhập Email/ Số điện thoại")
        password = self._get_value(self.reg_password, "Nhập mật khẩu")

        if not username or not contact or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin đăng ký.")
            return

        result = register_reader(username, contact, password)
        if result["success"]:
            messagebox.showinfo("Đăng ký thành công", result["message"] + "\nVui lòng đăng nhập.")
            self._build_login_form()
            self.login_identifier.delete(0, tk.END)
            self.login_identifier.config(fg=TEXT_DARK)
            self.login_identifier.insert(0, contact)
        else:
            messagebox.showerror("Đăng ký thất bại", result["message"])
