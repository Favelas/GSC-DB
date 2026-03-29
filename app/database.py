"""
database.py — Gestión Solar del Caribe S.A.S.
Auto-migración versionada. NUNCA destruye datos existentes.
Versión 2.0
"""

import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_path="solar_caribe.db"):
        self.db_path = db_path
        self._inicializar_db()

    # ─────────────────────────────────────────────
    # CONEXIÓN
    # ─────────────────────────────────────────────

    def _conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ─────────────────────────────────────────────
    # INICIALIZACIÓN Y MIGRACIONES
    # ─────────────────────────────────────────────

    def _inicializar_db(self):
        """Crea tablas base y aplica migraciones automáticas."""
        with self._conectar() as conn:
            cur = conn.cursor()

            # ── CLIENTES ──────────────────────────────────────────
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_titular    TEXT NOT NULL,
                    cedula_nit        TEXT UNIQUE NOT NULL
                )
            """)
            self._migrar(cur, "clientes", {
                "direccion_completa": "TEXT",
                "barrio_sector":      "TEXT",
                "estrato":            "INTEGER",
                "geolocalizacion":    "TEXT",
                "tarifa_aire_actual": "REAL DEFAULT 0",
                "tarifa_gsc":         "REAL DEFAULT 0",
                "telefono":           "TEXT",
                "email":              "TEXT",
            })

            # ── PROYECTOS ─────────────────────────────────────────
            cur.execute("""
                CREATE TABLE IF NOT EXISTS proyectos (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id       INTEGER,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            """)
            self._migrar(cur, "proyectos", {
                "nombre_proyecto":        "TEXT",
                "fecha_instalacion":      "DATE",
                "kwp_instalados":         "REAL",
                "marca_paneles":          "TEXT",
                "seriales_paneles":       "TEXT",
                "marca_inversor":         "TEXT",
                "serial_inversor":        "TEXT",
                "capacidad_inversor_kw":  "REAL DEFAULT 3.0",
                "estatus_retie":          "TEXT DEFAULT 'Pendiente'",
                "ruta_fotos_entrega":     "TEXT",
            })

            # ── CONSUMOS ──────────────────────────────────────────
            cur.execute("""
                CREATE TABLE IF NOT EXISTS consumos (
                    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id            INTEGER NOT NULL,
                    mes                   INTEGER NOT NULL,
                    anio                  INTEGER NOT NULL,
                    kwh_consumidos        REAL DEFAULT 0,
                    lectura_medidor_red   REAL DEFAULT 0,
                    subsidio_aire         REAL DEFAULT 0,
                    deducciones_aire      REAL DEFAULT 0,
                    fecha_registro        TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            """)

            # ── MANTENIMIENTOS ────────────────────────────────────
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mantenimientos (
                    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
                    proyecto_id           INTEGER NOT NULL,
                    fecha_visita          TEXT NOT NULL,
                    tecnico_encargado     TEXT,
                    estado_estructura     INTEGER DEFAULT 3,
                    estado_cableado       INTEGER DEFAULT 3,
                    limpieza_paneles      INTEGER DEFAULT 0,
                    continuidad_tierra_ohm REAL DEFAULT 0,
                    ruta_fotos            TEXT,
                    ruta_acta_pdf         TEXT,
                    observaciones_criticas TEXT,
                    fecha_registro        TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
                )
            """)

            # ── USUARIOS ──────────────────────────────────────────
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id              INTEGER PRIMARY KEY,
                    usuario         TEXT UNIQUE,
                    password        TEXT,
                    nombre_completo TEXT
                )
            """)
            if cur.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO usuarios (usuario, password, nombre_completo) "
                    "VALUES ('admin', 'admin123', 'Administrador GSC')"
                )

            conn.commit()

    def _migrar(self, cursor, tabla: str, columnas: dict):
        """Agrega columnas que no existan. Nunca borra nada."""
        cursor.execute(f"PRAGMA table_info({tabla})")
        existentes = {row[1] for row in cursor.fetchall()}
        for col, tipo in columnas.items():
            if col not in existentes:
                cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo}")

    # ─────────────────────────────────────────────
    # CLIENTES
    # ─────────────────────────────────────────────

    def obtener_clientes(self, busqueda: str = ""):
        with self._conectar() as conn:
            if busqueda:
                like = f"%{busqueda}%"
                rows = conn.execute(
                    "SELECT * FROM clientes "
                    "WHERE nombre_titular LIKE ? OR cedula_nit LIKE ? OR telefono LIKE ? "
                    "ORDER BY nombre_titular",
                    (like, like, like)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM clientes ORDER BY nombre_titular"
                ).fetchall()
            return [dict(r) for r in rows]

    def obtener_cliente_por_id(self, cid: int):
        with self._conectar() as conn:
            r = conn.execute("SELECT * FROM clientes WHERE id=?", (cid,)).fetchone()
            return dict(r) if r else None

    def crear_cliente(self, d: dict) -> int:
        with self._conectar() as conn:
            cur = conn.execute("""
                INSERT INTO clientes (
                    nombre_titular, cedula_nit, direccion_completa,
                    barrio_sector, estrato, geolocalizacion,
                    tarifa_aire_actual, tarifa_gsc, telefono, email
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                d.get("nombre"), d.get("nit"), d.get("dir"),
                d.get("barrio"), d.get("estrato") or None,
                d.get("geo"), d.get("tarifa") or 0,
                d.get("tarifa_gsc") or 0, d.get("tel"), d.get("mail"),
            ))
            conn.commit()
            return cur.lastrowid

    def actualizar_cliente(self, cid: int, d: dict):
        with self._conectar() as conn:
            conn.execute("""
                UPDATE clientes SET
                    nombre_titular=?, cedula_nit=?, direccion_completa=?,
                    barrio_sector=?, estrato=?, geolocalizacion=?,
                    tarifa_aire_actual=?, tarifa_gsc=?, telefono=?, email=?
                WHERE id=?
            """, (
                d.get("nombre"), d.get("nit"), d.get("dir"),
                d.get("barrio"), d.get("estrato") or None,
                d.get("geo"), d.get("tarifa") or 0,
                d.get("tarifa_gsc") or 0, d.get("tel"), d.get("mail"),
                cid,
            ))
            conn.commit()

    # ─────────────────────────────────────────────
    # PROYECTOS
    # ─────────────────────────────────────────────

    def obtener_proyectos(self, cliente_id: int = None):
        with self._conectar() as conn:
            if cliente_id:
                rows = conn.execute("""
                    SELECT p.*, c.nombre_titular as cliente_nombre,
                           c.tarifa_aire_actual, c.tarifa_gsc
                    FROM proyectos p
                    JOIN clientes c ON p.cliente_id = c.id
                    WHERE p.cliente_id = ?
                    ORDER BY p.id DESC
                """, (cliente_id,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT p.*, c.nombre_titular as cliente_nombre,
                           c.tarifa_aire_actual, c.tarifa_gsc
                    FROM proyectos p
                    JOIN clientes c ON p.cliente_id = c.id
                    ORDER BY p.id DESC
                """).fetchall()
            return [dict(r) for r in rows]

    def obtener_proyecto_por_id(self, pid: int):
        with self._conectar() as conn:
            r = conn.execute("""
                SELECT p.*, c.nombre_titular as cliente_nombre,
                       c.tarifa_aire_actual, c.tarifa_gsc
                FROM proyectos p
                JOIN clientes c ON p.cliente_id = c.id
                WHERE p.id=?
            """, (pid,)).fetchone()
            return dict(r) if r else None

    def crear_proyecto(self, d: dict) -> int:
        with self._conectar() as conn:
            cur = conn.execute("""
                INSERT INTO proyectos (
                    cliente_id, nombre_proyecto, fecha_instalacion,
                    kwp_instalados, marca_paneles, seriales_paneles,
                    marca_inversor, serial_inversor, capacidad_inversor_kw,
                    estatus_retie, ruta_fotos_entrega
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (
                d.get("cliente_id"), d.get("nombre"),
                d.get("fecha_instalacion") or __import__("datetime").date.today().isoformat(),
                d.get("kwp"), d.get("paneles"), d.get("seriales"),
                d.get("inversor"), d.get("serial_inversor"),
                d.get("capacidad_inversor_kw") or 3.0,
                d.get("retie", "Pendiente"), d.get("ruta_fotos"),
            ))
            conn.commit()
            return cur.lastrowid

    def actualizar_proyecto(self, pid: int, d: dict):
        with self._conectar() as conn:
            conn.execute("""
                UPDATE proyectos SET
                    nombre_proyecto=?, fecha_instalacion=?,
                    kwp_instalados=?, marca_paneles=?, seriales_paneles=?,
                    marca_inversor=?, serial_inversor=?, capacidad_inversor_kw=?,
                    estatus_retie=?, ruta_fotos_entrega=?
                WHERE id=?
            """, (
                d.get("nombre"), d.get("fecha_instalacion"),
                d.get("kwp"), d.get("paneles"), d.get("seriales"),
                d.get("inversor"), d.get("serial_inversor"),
                d.get("capacidad_inversor_kw") or 3.0,
                d.get("retie", "Pendiente"), d.get("ruta_fotos"),
                pid,
            ))
            conn.commit()

    # ─────────────────────────────────────────────
    # CONSUMOS
    # ─────────────────────────────────────────────

    def obtener_consumos(self, cliente_id: int = None):
        with self._conectar() as conn:
            if cliente_id:
                rows = conn.execute("""
                    SELECT co.*, c.nombre_titular, c.tarifa_aire_actual, c.tarifa_gsc
                    FROM consumos co
                    JOIN clientes c ON co.cliente_id = c.id
                    WHERE co.cliente_id=?
                    ORDER BY co.anio DESC, co.mes DESC
                """, (cliente_id,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT co.*, c.nombre_titular, c.tarifa_aire_actual, c.tarifa_gsc
                    FROM consumos co
                    JOIN clientes c ON co.cliente_id = c.id
                    ORDER BY co.anio DESC, co.mes DESC
                """).fetchall()
            return [dict(r) for r in rows]

    def crear_consumo(self, d: dict) -> int:
        with self._conectar() as conn:
            cur = conn.execute("""
                INSERT INTO consumos (
                    cliente_id, mes, anio, kwh_consumidos,
                    lectura_medidor_red, subsidio_aire, deducciones_aire
                ) VALUES (?,?,?,?,?,?,?)
            """, (
                d["cliente_id"], d["mes"], d["anio"],
                d.get("kwh_consumidos", 0), d.get("lectura_medidor_red", 0),
                d.get("subsidio_aire", 0), d.get("deducciones_aire", 0),
            ))
            conn.commit()
            return cur.lastrowid

    # ─────────────────────────────────────────────
    # MANTENIMIENTOS
    # ─────────────────────────────────────────────

    def obtener_mantenimientos(self, proyecto_id: int = None):
        with self._conectar() as conn:
            if proyecto_id:
                rows = conn.execute("""
                    SELECT m.*, c.nombre_titular
                    FROM mantenimientos m
                    JOIN proyectos p ON m.proyecto_id = p.id
                    JOIN clientes c ON p.cliente_id = c.id
                    WHERE m.proyecto_id=?
                    ORDER BY m.fecha_visita DESC
                """, (proyecto_id,)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT m.*, c.nombre_titular
                    FROM mantenimientos m
                    JOIN proyectos p ON m.proyecto_id = p.id
                    JOIN clientes c ON p.cliente_id = c.id
                    ORDER BY m.fecha_visita DESC
                """).fetchall()
            return [dict(r) for r in rows]

    def obtener_mantenimiento_por_id(self, mid: int):
        with self._conectar() as conn:
            r = conn.execute("""
                SELECT m.*, c.nombre_titular
                FROM mantenimientos m
                JOIN proyectos p ON m.proyecto_id = p.id
                JOIN clientes c ON p.cliente_id = c.id
                WHERE m.id=?
            """, (mid,)).fetchone()
            return dict(r) if r else None

    def crear_mantenimiento(self, d: dict) -> int:
        with self._conectar() as conn:
            cur = conn.execute("""
                INSERT INTO mantenimientos (
                    proyecto_id, fecha_visita, tecnico_encargado,
                    estado_estructura, estado_cableado, limpieza_paneles,
                    continuidad_tierra_ohm, ruta_fotos, ruta_acta_pdf,
                    observaciones_criticas
                ) VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                d["proyecto_id"], d["fecha_visita"], d.get("tecnico_encargado"),
                d.get("estado_estructura", 3), d.get("estado_cableado", 3),
                1 if d.get("limpieza_paneles") else 0,
                d.get("continuidad_tierra_ohm", 0),
                d.get("ruta_fotos"), d.get("ruta_acta_pdf"),
                d.get("observaciones_criticas"),
            ))
            conn.commit()
            return cur.lastrowid

    # ─────────────────────────────────────────────
    # DASHBOARD KPIs
    # ─────────────────────────────────────────────

    def obtener_kpis(self) -> dict:
        with self._conectar() as conn:
            kwp = conn.execute(
                "SELECT COALESCE(SUM(kwp_instalados),0) FROM proyectos"
            ).fetchone()[0]
            clientes = conn.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
            proyectos = conn.execute("SELECT COUNT(*) FROM proyectos").fetchone()[0]
            retie_pend = conn.execute(
                "SELECT COUNT(*) FROM proyectos WHERE estatus_retie='Pendiente'"
            ).fetchone()[0]

            # Próximos mantenimientos (sin visita en +6 meses o nunca)
            alertas = conn.execute("""
                SELECT p.id, c.nombre_titular, c.telefono,
                       MAX(m.fecha_visita) as ultimo_mant
                FROM proyectos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN mantenimientos m ON m.proyecto_id = p.id
                GROUP BY p.id
                HAVING ultimo_mant IS NULL
                    OR date(ultimo_mant) <= date('now','-6 months')
                ORDER BY ultimo_mant ASC
                LIMIT 8
            """).fetchall()

            return {
                "kwp":        round(kwp, 2),
                "clientes":   clientes,
                "proyectos":  proyectos,
                "retie_pend": retie_pend,
                "alertas":    [dict(r) for r in alertas],
            }

    # ─────────────────────────────────────────────
    # EXPORTACIÓN
    # ─────────────────────────────────────────────

    def exportar_tabla(self, tabla: str):
        """Devuelve (columnas, filas) para exportar cualquier tabla."""
        tablas_validas = {"clientes", "proyectos", "consumos", "mantenimientos"}
        if tabla not in tablas_validas:
            raise ValueError(f"Tabla '{tabla}' no permitida.")
        with self._conectar() as conn:
            rows = conn.execute(f"SELECT * FROM {tabla}").fetchall()
            if not rows:
                return [], []
            return list(rows[0].keys()), [dict(r) for r in rows]

    # ─────────────────────────────────────────────
    # HISTÓRICO PARA GRÁFICO (módulo expediente)
    # ─────────────────────────────────────────────

    def obtener_datos_grafico_cliente(self, cliente_id: int):
        with self._conectar() as conn:
            rows = conn.execute("""
                SELECT mes, anio, kwh_consumidos
                FROM consumos
                WHERE cliente_id=?
                ORDER BY anio, mes
                LIMIT 12
            """, (cliente_id,)).fetchall()
            return [dict(r) for r in rows]

    # ─────────────────────────────────────────────
    # LEGACY: historial_consumo (compatibilidad)
    # ─────────────────────────────────────────────

    def obtener_historial_cliente(self, cliente_id: int):
        """Alias para compatibilidad con módulos antiguos."""
        rows = self.obtener_consumos(cliente_id)
        # Normalizar clave mes_ano para módulos que la usen
        for r in rows:
            r["mes_ano"] = f"{r['anio']}-{str(r['mes']).zfill(2)}"
            r["lectura_inversor_gsc"] = r.get("kwh_consumidos", 0)
            r["lectura_medidor_red"]  = r.get("lectura_medidor_red", 0)
            r["subsidio_red_aplicado"] = r.get("subsidio_aire", 0)
            r["valor_base_gsc"] = 0
        return rows

    # ─────────────────────────────────────────────
    # LOGIN
    # ─────────────────────────────────────────────

    def verify_login(self, usuario: str, password: str):
        with self._conectar() as conn:
            r = conn.execute(
                "SELECT * FROM usuarios WHERE usuario=? AND password=?",
                (usuario, password)
            ).fetchone()
            return dict(r) if r else None
