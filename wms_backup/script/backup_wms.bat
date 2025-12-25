@echo off

set DATE=%DATE:~-4%-%DATE:~3,2%-%DATE:~0,2%
set TIME=%TIME:~0,2%-%TIME:~3,2%

set BACKUP_DIR=C:\wms_backup\backups
set LOG_FILE=C:\wms_backup\logs\backup.log

echo [%DATE% %TIME%] Debut sauvegarde WMS >> %LOG_FILE%

cd "C:\Program Files\MySQL\MySQL Server 8.0\bin"

REM Sauvegarde SQL
mysqldump -u root -p wms_db > %BACKUP_DIR%\backup_wms_%DATE%_%TIME%.sql
IF ERRORLEVEL 1 (
  echo [%DATE% %TIME%] ERREUR sauvegarde SQL >> %LOG_FILE%
  exit /b 1
)

REM Export CSV
mysql -u root -p wms_db -e "SELECT id, order_ref, created_at FROM orders" --batch --raw > %BACKUP_DIR%\orders_%DATE%_%TIME%.csv
IF ERRORLEVEL 1 (
  echo [%DATE% %TIME%] ERREUR export CSV >> %LOG_FILE%
  exit /b 1
)

echo [%DATE% %TIME%] Sauvegarde OK >> %LOG_FILE%
exit /b 0
