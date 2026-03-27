"""
Ventana de Login — Gestión Solar del Caribe S.A.S.
"""

import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS


class LoginWindow(ctk.CTk):
    """Ventana de autenticación inicial."""

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.current_user = None

        self._configurar_ventana()
        self._construir_ui()
        self.after(100, lambda: self.entry_user.focus())

    def _configurar_ventana(self):
        self.title("Solar Caribe — Login")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_primary"])
        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = (self.winfo_screenheight() - 560) // 2
        self.geometry(f"480x560+{x}+{y}")

    def _construir_ui(self):
        # Fondo con tarjeta centrada
        main_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"],
            corner_radius=16,
            border_width=1, border_color=COLORS["border_primary"]
        )
        main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.88)

        # Logo / Ícono solar
        logo_label = ctk.CTkLabel(
            main_frame,
            text="☀",
            font=("Segoe UI Emoji", 52),
            text_color=COLORS["solar_yellow"]
        )
        logo_label.pack(pady=(36, 4))

        # Nombre empresa
        ctk.CTkLabel(
            main_frame,
            text="GESTIÓN SOLAR DEL CARIBE",
            font=FONTS["title_medium"],
            text_color=COLORS["accent_primary"]
        ).pack()

        ctk.CTkLabel(
            main_frame,
            text="S.A.S.",
            font=FONTS["body_medium"],
            text_color=COLORS["text_secondary"]
        ).pack()

        ctk.CTkLabel(
            main_frame,
            text="Sistema de Gestión Interna",
            font=FONTS["body_small"],
            text_color=COLORS["text_muted"]
        ).pack(pady=(2, 24))

        # Separador
        sep = ctk.CTkFrame(main_frame, height=1, fg_color=COLORS["border_primary"])
        sep.pack(fill="x", padx=30, pady=(0, 24))

        # Form frame
        form = ctk.CTkFrame(main_frame, fg_color="transparent")
        form.pack(fill="x", padx=30)

        # Usuario
        ctk.CTkLabel(form, text="Usuario", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_user = ctk.CTkEntry(
            form, placeholder_text="Ingrese su usuario",
            height=42, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_large"]
        )
        self.entry_user.pack(fill="x", pady=(4, 14))

        # Contraseña
        ctk.CTkLabel(form, text="Contraseña", font=FONTS["label"],
                     text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.entry_pass = ctk.CTkEntry(
            form, placeholder_text="Ingrese su contraseña",
            show="•", height=42, fg_color=COLORS["bg_input"],
            border_color=COLORS["border_primary"],
            text_color=COLORS["text_primary"],
            font=FONTS["body_large"]
        )
        self.entry_pass.pack(fill="x", pady=(4, 6))

        # Mensaje de error
        self.lbl_error = ctk.CTkLabel(
            form, text="", font=FONTS["body_small"],
            text_color=COLORS["danger"]
        )
        self.lbl_error.pack(pady=(0, 16))

        # Botón Login
        self.btn_login = ctk.CTkButton(
            form, text="  INGRESAR AL SISTEMA",
            height=44, corner_radius=8,
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color="#000000",
            font=FONTS["title_small"],
            command=self._intentar_login
        )
        self.btn_login.pack(fill="x")

        # Footer
        ctk.CTkLabel(
            main_frame,
            text="Usuario por defecto: admin / admin123",
            font=FONTS["caption"],
            text_color=COLORS["text_muted"]
        ).pack(pady=(20, 8))

        # Binds
        self.entry_pass.bind("<Return>", lambda e: self._intentar_login())
        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus())

    def _intentar_login(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()

        if not username or not password:
            self.lbl_error.configure(text="⚠  Por favor complete todos los campos.")
            return

        self.btn_login.configure(state="disabled", text="Verificando...")
        self.update()

        user = self.db.verify_login(username, password)

        if user:
            self.current_user = user
            self._abrir_app_principal()
        else:
            self.lbl_error.configure(text="✗  Credenciales incorrectas. Intente nuevamente.")
            self.btn_login.configure(state="normal", text="  INGRESAR AL SISTEMA")
            self.entry_pass.delete(0, "end")

    def _abrir_app_principal(self):
        from app.ui.main_window import MainWindow
        self.destroy()
        app = MainWindow(self.db, self.current_user)
        app.mainloop()
