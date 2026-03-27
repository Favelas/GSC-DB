import sys
import os
import customtkinter as ctk

# Configuración de Rutas para evitar errores de importación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app.database import DatabaseManager
from app.ui.login_window import LoginWindow

def main():
    """Punto de entrada principal de GSC App."""
    
    # Configuración de apariencia
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Inicialización de la base de datos
    db = DatabaseManager()
    
    # Iniciar con la ventana de Login
    try:
        login_app = LoginWindow(db)
        login_app.mainloop()
    except Exception as e:
        print(f"Error al ejecutar la interfaz: {e}")

if __name__ == "__main__":
    main()