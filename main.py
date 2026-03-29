"""
main.py — Gestión Solar del Caribe S.A.S.  v2.0
Punto de entrada principal.
"""

import sys
import os
import customtkinter as ctk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.database import DatabaseManager
from app.ui.login_window import LoginWindow


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    db = DatabaseManager()   # auto-migración en el constructor

    try:
        LoginWindow(db).mainloop()
    except Exception as e:
        print(f"Error al iniciar GSC: {e}")
        raise


if __name__ == "__main__":
    main()
