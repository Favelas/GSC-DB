"""
Constantes de diseño y tema para la aplicación Solar Caribe.
Paleta: Deep Blue/Dark con acentos Verde Esmeralda.
"""

# ==================== PALETA DE COLORES ====================
COLORS = {
    # Fondos principales
    "bg_primary":       "#0D1117",   # Fondo más oscuro
    "bg_secondary":     "#161B22",   # Sidebar y paneles
    "bg_card":          "#1C2333",   # Cards y formularios
    "bg_input":         "#21262D",   # Inputs
    "bg_hover":         "#2D3748",   # Hover states

    # Acentos - Verde Esmeralda
    "accent_primary":   "#00C896",   # Verde esmeralda principal
    "accent_hover":     "#00A87E",   # Verde hover
    "accent_dark":      "#007A5C",   # Verde oscuro
    "accent_glow":      "#00C89640", # Verde con transparencia (glow)

    # Texto
    "text_primary":     "#E6EDF3",   # Texto principal
    "text_secondary":   "#8B949E",   # Texto secundario
    "text_muted":       "#484F58",   # Texto muy apagado
    "text_accent":      "#00C896",   # Texto con acento

    # Estado
    "success":          "#3FB950",   # Verde éxito
    "warning":          "#D29922",   # Amarillo advertencia
    "danger":           "#F85149",   # Rojo peligro
    "info":             "#58A6FF",   # Azul info

    # Bordes
    "border_primary":   "#30363D",   # Borde normal
    "border_accent":    "#00C896",   # Borde con acento

    # Sidebar
    "sidebar_bg":       "#0D1117",
    "sidebar_hover":    "#1C2333",
    "sidebar_width":    220,

    # Especiales
    "solar_orange":     "#FF8C00",   # Color solar/energía
    "solar_yellow":     "#FFD700",   # Amarillo solar
}

# ==================== TIPOGRAFÍA ====================
FONTS = {
    "title_large":   ("Segoe UI", 22, "bold"),
    "title_medium":  ("Segoe UI", 16, "bold"),
    "title_small":   ("Segoe UI", 13, "bold"),
    "body_large":    ("Segoe UI", 12),
    "body_medium":   ("Segoe UI", 11),
    "body_small":    ("Segoe UI", 10),
    "mono":          ("Consolas", 11),
    "label":         ("Segoe UI", 11, "bold"),
    "caption":       ("Segoe UI", 9),
    "kpi":           ("Segoe UI", 28, "bold"),
    "kpi_small":     ("Segoe UI", 18, "bold"),
}

# ==================== DIMENSIONES ====================
DIMENSIONS = {
    "sidebar_width":       220,
    "header_height":       60,
    "card_padding":        20,
    "button_height":       38,
    "input_height":        36,
    "border_radius":       8,
    "window_min_width":    1100,
    "window_min_height":   680,
}

# ==================== TABLAS EXPORTABLES ====================
TABLAS_EXPORTABLES = {
    "Clientes":               "Clientes",
    "Proyectos_Instalacion":  "Proyectos de Instalación",
    "Historial_Consumo":      "Historial de Consumo",
    "Mantenimientos":         "Mantenimientos",
}

# ==================== NAVEGACIÓN ====================
NAV_ITEMS = [
    {"id": "dashboard",      "label": "Dashboard",      "icon": "⚡"},
    {"id": "clientes",       "label": "Clientes",       "icon": "👤"},
    {"id": "proyectos",      "label": "Proyectos",      "icon": "🔧"},
    {"id": "historial",      "label": "Consumo",        "icon": "📊"},
    {"id": "mantenimientos", "label": "Mantenimientos", "icon": "🛠"},
    {"id": "expediente",     "label": "Expedientes",    "icon": "📁"},
    {"id": "exportar",       "label": "Exportar",       "icon": "📤"},
]