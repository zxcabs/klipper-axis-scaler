#!/usr/bin/env bash

SRCDIR="$( cd "$( dirname "${BASH_SOURCE}" )" && pwd )"
# Создаем отдельную независимую папку для кастомных компонентов
DEST_DIR="/home/mks/printer_data/config"

echo "=== Установка Axis Scaler для FreeDi ==="
mkdir -p "$DEST_DIR"

# Создаем символическую ссылку в нашу новую чистую папку
ln -sf "${SRCDIR}/axis_scaler.py" "${DEST_DIR}/axis_scaler.py"

echo "Перезапуск Moonraker..."
sudo systemctl restart moonraker
echo "Установка завершена!"
