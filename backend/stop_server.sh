#!/bin/bash
PID=$(ps aux | grep "[u]vicorn admin_api:app" | awk '{print $2}')
if [ -z "$PID" ]; then
    echo "❌ Aucun serveur en cours"
else
    echo "✅ Arrêt du serveur (PID: $PID)"
    kill $PID
fi
