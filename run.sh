#!/bin/bash
# Script de Reactivación Rápida de Infraestructura para Bounty Hunter AI
# Uso: ./run.sh

echo "=========================================================="
echo "⚡ [BOUNTY HUNTER AI] - ACTIVANDO INFRAESTRUCTURA..."
echo "=========================================================="

# 1. Detener procesos previos que puedan estar usando los puertos
echo "[*] Limpiando procesos previos..."
pkill -f "http.server 8000"
pkill -f "hourly_audit_daemon.py"

# 2. Levantar Servidor Web del Dashboard en puerto 8000
echo "[+] Iniciando Servidor Web en http://localhost:8000/..."
python3 -m http.server 8000 --directory dashboard > /dev/null 2>&1 &
SERVER_PID=$!

# 3. Levantar Daemon de Auditoría y Búsqueda Horaria
echo "[+] Iniciando Daemon de Auditoría Horaria..."
python3 -u tools/hourly_audit_daemon.py > tools/hourly_daemon.log 2>&1 &
DAEMON_PID=$!

sleep 2

# 4. Mostrar estado actual
echo "=========================================================="
echo "✅ ¡INFRAESTRUCTURA ONLINE!"
echo "=========================================================="
echo "👉 Dashboard Local: http://localhost:8000/"
echo "👉 PID Servidor Web: $SERVER_PID"
echo "👉 PID Daemon Horario: $DAEMON_PID (Log en tools/hourly_daemon.log)"
echo "=========================================================="
