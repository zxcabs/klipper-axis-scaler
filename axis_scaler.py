#!/usr/bin/env python3
import sys
import os
import re

def main():
    if len(sys.argv) < 2:
        print("Ошибка: Не указан путь к G-код файлу")
        return

    file_path = sys.argv[-1]

    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 1. Защита: ищем флаг в последних 20 строках файла (так как он теперь в конце)
    for line in lines[-20:]:
        if "pre_scale_preprocessored" in line:
            print("AxisScaler: [ПРОПУСК] Файл уже был масштабирован ранее.")
            return

    scale_x, scale_y, scale_z = 1.0, 1.0, 1.0
    params_found = False
    
    # 2. Ищем параметры масштабирования в первых 1000 строках
    for line in lines[:1000]:
        if "pre_scale_x" in line:
            match = re.search(r'pre_scale_x\s*=\s*([\d.]+)', line)
            if match: scale_x = float(match.group(1)); params_found = True
        if "pre_scale_y" in line:
            match = re.search(r'pre_scale_y\s*=\s*([\d.]+)', line)
            if match: scale_y = float(match.group(1)); params_found = True
        if "pre_scale_z" in line:
            match = re.search(r'pre_scale_z\s*=\s*([\d.]+)', line)
            if match: scale_z = float(match.group(1)); params_found = True

    if not params_found or (scale_x == 1.0 and scale_y == 1.0 and scale_z == 1.0):
        print("AxisScaler: [НЕТ МЕТОК] Коэффициенты усадки в файле не обнаружены.")
        return

    print(f"AxisScaler: [ОБРАБОТКА] Масштабирование файла. Коэффициенты: X:{scale_x}, Y:{scale_y}, Z:{scale_z}")

    x_re = re.compile(r'([X])([-+]?\d*\.\d+|\d+)')
    y_re = re.compile(r'([Y])([-+]?\d*\.\d+|\d+)')
    z_re = re.compile(r'([Z])([-+]?\d*\.\d+|\d+)')

    new_lines = []
    for line in lines:
        if line.strip().startswith(';') or "EXCLUDE_OBJECT" in line or any(cmd in line for cmd in ['M10', 'M14', 'M19']):
            new_lines.append(line)
            continue

        mod_line = line
        if scale_x != 1.0: mod_line = x_re.sub(lambda m: f"X{round(float(m.group(2)) * scale_x, 4)}", mod_line)
        if scale_y != 1.0: mod_line = y_re.sub(lambda m: f"Y{round(float(m.group(2)) * scale_y, 4)}", mod_line)
        if scale_z != 1.0: mod_line = z_re.sub(lambda m: f"Z{round(float(m.group(2)) * scale_z, 4)}", mod_line)
        new_lines.append(mod_line)

    # 3. Дописываем маркер успешной обработки в самый конец файла
    new_lines.append(f"\n; pre_scale_preprocessored (X:{scale_x} Y:{scale_y} Z:{scale_z})\n")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("AxisScaler: [УСПЕХ] Файл G-кода успешно пересчитан!")

if __name__ == '__main__':
    main()
