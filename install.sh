#!/usr/bin/env bash

# Скрипт автоматической установки плагина AxisScaler в систему Moonraker
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MOONRAKER_EXT_DIR="${HOME}/moonraker/moonraker/components"

echo "=== Установка Moonraker Axis Scaler ==="

# Проверяем, существует ли папка компонентов Moonraker
if [ ! -d "$MOONRAKER_EXT_DIR" ]; then
    echo "Ошибка: Директория компонентов Moonraker не найдена по пути $MOONRAKER_EXT_DIR"
    exit 1
fi

# Создаем символическую ссылку на файл плагина
echo "Создание символической ссылки для axis_scaler.py..."
ln -sf "${SRCDIR}/axis_scaler.py" "${MOONRAKER_EXT_DIR}/axis_scaler.py"

# Перезапускаем сервис Moonraker для применения изменений
echo "Перезапуск сервиса Moonraker..."
sudo systemctl restart moonraker

echo "Установка успешно завершена!"
