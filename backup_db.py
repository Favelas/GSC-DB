"""
Script de Respaldo Manual para Gestión Solar del Caribe.
Copia la base de datos a una carpeta de seguridad con fecha y hora.
"""
import shutil
import os
from datetime import datetime

def ejecutar_respaldo():
    # Nombre de tu base de datos actual
    db_origen = "solar_caribe.db"
    
    # Crear carpeta de backups si no existe
    carpeta_backup = "backups_gsc"
    if not os.path.exists(carpeta_backup):
        os.makedirs(carpeta_backup)
        print(f"Carpeta '{carpeta_backup}' creada.")

    if os.path.exists(db_origen):
        # Generar nombre con fecha: BACKUP_20260326_1430_solar_caribe.db
        fecha_hora = datetime.now().strftime("%Y%m%d_%H%M")
        db_destino = os.path.join(carpeta_backup, f"BACKUP_{fecha_hora}_{db_origen}")
        
        # Copiar archivo
        shutil.copy2(db_origen, db_destino)
        print(f"✅ Respaldo exitoso: {db_destino}")
        return True
    else:
        print("❌ Error: No se encontró la base de datos original.")
        return False

if __name__ == "__main__":
    ejecutar_respaldo()