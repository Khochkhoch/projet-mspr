import subprocess
from datetime import datetime
import os

# ===== CONFIG =====
MYSQL_USER = "root"          # ou l’utilisateur qui vient de marcher
MYSQL_PASSWORD = "06122001"
DB_NAME = "wms_db"


MYSQL_BIN = r"C:\Program Files\MySQL\MySQL Server 8.0\bin"
BACKUP_DIR = r"C:\wms_backup\backups"
LOG_FILE = r"C:\wms_backup\logs\backup.log"

# ==================

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

now = datetime.now()
date_str = now.strftime("%Y-%m-%d_%H-%M")

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{date_str}] {message}\n")

log("Début sauvegarde WMS")

try:
    # Sauvegarde SQL
    sql_file = f"{BACKUP_DIR}\\backup_wms_{date_str}.sql"
    subprocess.run(
        subprocess.run(
    [f"{MYSQL_BIN}\\mysqldump", "-u", MYSQL_USER, f"-p{MYSQL_PASSWORD}", DB_NAME],
    stdout=open(sql_file, "w"),
    check=True
)
    )

    # Export CSV
    csv_file = f"{BACKUP_DIR}\\orders_{date_str}.csv"
    subprocess.run(
    [
        f"{MYSQL_BIN}\\mysql",
        "-u", MYSQL_USER,
        f"-p{MYSQL_PASSWORD}",
        DB_NAME,
        "-e", "SELECT id, order_ref, created_at FROM orders"
    ],
    stdout=open(csv_file, "w"),
    check=True
)


    log("Sauvegarde OK")

except Exception as e:
    log(f"ERREUR sauvegarde : {e}")
