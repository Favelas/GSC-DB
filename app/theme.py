"""
theme.py — Gestión Solar del Caribe S.A.S.
Paleta: Deep Blue/Dark con acentos Verde Esmeralda.
"""

COLORS = {
    "bg_primary":     "#0D1117",
    "bg_secondary":   "#161B22",
    "bg_card":        "#1C2333",
    "bg_input":       "#21262D",
    "bg_hover":       "#2D3748",

    "accent_primary": "#00C896",
    "accent_hover":   "#00A87E",
    "accent_dark":    "#007A5C",

    "text_primary":   "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":     "#484F58",
    "text_accent":    "#00C896",

    "success":        "#3FB950",
    "warning":        "#D29922",
    "danger":         "#F85149",
    "info":           "#58A6FF",

    "border_primary": "#30363D",
    "border_accent":  "#00C896",

    "sidebar_bg":     "#0D1117",
    "sidebar_hover":  "#1C2333",
    "sidebar_width":  240,

    "solar_orange":   "#FF8C00",
    "solar_yellow":   "#FFD700",
}

FONTS = {
    "title_large":  ("Segoe UI", 22, "bold"),
    "title_medium": ("Segoe UI", 16, "bold"),
    "title_small":  ("Segoe UI", 13, "bold"),
    "body_large":   ("Segoe UI", 12),
    "body_medium":  ("Segoe UI", 11),
    "body_small":   ("Segoe UI", 10),
    "mono":         ("Consolas", 11),
    "label":        ("Segoe UI", 11, "bold"),
    "caption":      ("Segoe UI", 9),
    "kpi":          ("Segoe UI", 28, "bold"),
    "kpi_small":    ("Segoe UI", 18, "bold"),
}

DIMENSIONS = {
    "sidebar_width":    240,
    "header_height":    60,
    "card_padding":     20,
    "button_height":    38,
    "input_height":     36,
    "border_radius":    8,
    "window_min_width":  1100,
    "window_min_height": 680,
}

# Tablas disponibles para exportar a Excel
TABLAS_EXPORTABLES = {
    "clientes":       "Clientes",
    "proyectos":      "Proyectos de Instalación",
    "consumos":       "Historial de Consumo",
    "mantenimientos": "Mantenimientos",
}

NAV_ITEMS = [
    {"id": "dashboard",      "label": "Dashboard",      "icon": "⚡"},
    {"id": "clientes",       "label": "Clientes",       "icon": "👤"},
    {"id": "proyectos",      "label": "Proyectos",      "icon": "🔧"},
    {"id": "consumos",       "label": "Consumo",        "icon": "📊"},
    {"id": "mantenimientos", "label": "Mantenimientos", "icon": "🛠"},
    {"id": "expediente",     "label": "Expedientes",    "icon": "📁"},
    {"id": "exportar",       "label": "Exportar / PDF", "icon": "📤"},
]
