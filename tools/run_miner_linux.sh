#!/usr/bin/env bash
# Doomsday 24/7 VPS Miner - Dexter Rig 2 (Linux)
set -u

WORKER_NAME="${1:-Dexter-Linux-VPS-Rig-2}"

echo "========================================================"
echo "  DOOMSDAY 24/7 MINER FOR LINUX VPS"
echo "  Worker Address: doom162df6bb0c219de72343658ec04c1d9b1939c3c5c02f6b94f"
echo "  Settlement: 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20"
echo "  Rig Tag: ${WORKER_NAME}"
echo "========================================================"

while true; do
    echo "[$(date)] Starting Doomsday Miner..."
    ./doomsday_miner_linux_x64 -worker "${WORKER_NAME}"
    echo "[$(date)] Miner stopped or disconnected. Restarting in 5s..."
    sleep 5
done
