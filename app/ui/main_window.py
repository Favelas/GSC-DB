import customtkinter as ctk
from tkinter import messagebox
from app.theme import COLORS, FONTS, NAV_ITEMS, DIMENSIONS

# Importaciones de tus módulos de interfaz (Rutas verificadas según tus capturas)
from app.ui.dashboard import DashboardPage
from app.ui.clientes import ClientesPage
from app.ui.proyectos import ProyectosPage

class MainWindow(ctk.CTk):
    def __init__(self, db, user: dict):
        super().__init__()
        
        # Inyectar dependencias
        self.db = db
        self.user = user
        self.nav_buttons = {}
        
        # --- Configuración de Ventana ---
        self.title("GSC S.A.S. - Gestión Solar del Caribe")
        self.geometry("1280x720")
        self.configure(fg_color=COLORS["bg_primary"])
        
        # Centrar ventana en pantalla
        self._centrar_ventana(1280, 720)

        # --- Layout Principal ---
        # 1. Sidebar (Menú Lateral)
        self._construir_sidebar()
        
        # 2. Contenedor de Contenido (Lado derecho)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True)
        
        # 3. Pantalla inicial por defecto
        self._navegar("dashboard")

    def _centrar_ventana(self, ancho, alto):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def _construir_sidebar(self):
        """Crea el menú lateral basado en NAV_ITEMS de theme.py"""
        self.sidebar = ctk.CTkFrame(
            self, 
            width=240, 
            fg_color=COLORS["sidebar_bg"], 
            corner_radius=0,
            border_width=1,
            border_color=COLORS["border_primary"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Encabezado del Sidebar (Logo/Nombre)
        ctk.CTkLabel(
            self.sidebar, 
            text="☀", 
            font=("Segoe UI Emoji", 40),
            text_color=COLORS["solar_yellow"]
        ).pack(pady=(30, 0))

        ctk.CTkLabel(
            self.sidebar, 
            text="SOLAR CARIBE", 
            font=FONTS["title_medium"], 
            text_color=COLORS["accent_primary"]
        ).pack(pady=(0, 40))

        # Generación dinámica de botones
        for item in NAV_ITEMS:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {item['icon']}   {item['label']}",
                font=FONTS["body_large"],
                height=48,
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_hover"],
                anchor="w",
                corner_radius=8,
                command=lambda k=item["id"]: self._navegar(k)
            )
            btn.pack(fill="x", padx=15, pady=4)
            self.nav_buttons[item["id"]] = btn

        # Info del Usuario en la parte inferior
        self._construir_user_footer()

    def _construir_user_footer(self):
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=20, padx=15)
        
        line = ctk.CTkFrame(footer, height=1, fg_color=COLORS["border_primary"])
        line.pack(fill="x", pady=(0, 15))

        user_name = self.user.get('nombre_completo', 'Usuario')
        ctk.CTkLabel(footer, text=user_name, font=FONTS["body_medium"], text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(footer, text="Sesión: Activa", font=FONTS["caption"], text_color=COLORS["success"]).pack(anchor="w")

    def _navegar(self, key):
        """Maneja el cambio de pantallas y la estética de los botones."""
        # 1. Resaltar botón seleccionado
        for k, b in self.nav_buttons.items():
            if k == key:
                b.configure(fg_color=COLORS["bg_hover"], text_color=COLORS["accent_primary"])
            else:
                b.configure(fg_color="transparent", text_color=COLORS["text_secondary"])
            
        # 2. Limpiar el contenedor actual
        for child in self.container.winfo_children(): 
            child.destroy()

        # 3. Instanciar la página correspondiente
        try:
            if key == "dashboard":
                DashboardPage(self.container, self.db).pack(fill="both", expand=True)
            elif key == "clientes":
                ClientesPage(self.container, self.db).pack(fill="both", expand=True)
            elif key == "proyectos":
                ProyectosPage(self.container, self.db).pack(fill="both", expand=True)
            else:
                # Fallback para módulos que aún no has terminado de codear
                lbl = ctk.CTkLabel(self.container, text=f"Módulo '{key}' en desarrollo...", font=FONTS["title_medium"])
                lbl.pack(expand=True)
        except Exception as e:
            messagebox.showerror("Error de Navegación", f"No se pudo cargar la página: {e}")

if __name__ == "__main__":
    # Solo para pruebas rápidas aisladas si fuera necesario
    print("MainWindow debe ser ejecutado desde main.py")