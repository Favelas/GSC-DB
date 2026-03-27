import customtkinter as ctk
from app.theme import COLORS, FONTS

class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self._cargar_ui()

    def _cargar_ui(self):
        kpis = self.db.obtener_kpis()
        ctk.CTkLabel(self, text="⚡ GESTIÓN SOLAR DEL CARIBE", font=FONTS["title_large"], text_color=COLORS["accent_primary"]).pack(pady=30)
        
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=50)

        for txt, val, col in [("CLIENTES", kpis["clientes"], COLORS["solar_yellow"]), ("TOTAL kWp", f"{kpis['kwp']} kW", COLORS["accent_primary"])]:
            c = ctk.CTkFrame(cards, fg_color=COLORS["bg_card"], width=280, height=130)
            c.pack(side="left", padx=20, expand=True); c.pack_propagate(False)
            ctk.CTkLabel(c, text=txt, font=FONTS["label"]).pack(pady=(20,0))
            ctk.CTkLabel(c, text=str(val), font=FONTS["kpi"], text_color=col).pack()