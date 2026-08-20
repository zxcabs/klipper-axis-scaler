import os
import re
import logging
from utils import ServerError

# Создаем объект логгера для нашего компонента
logger = logging.getLogger("moonraker.axis_scaler")

class AxisScaler:
    def __init__(self, config):
        self.server = config.get_server()
        # Подписываемся на состояние печати
        self.server.register_notification("print_manager:state_changed", self._on_print_state_changed)
        logger.info("Плагин AxisScaler успешно инициализирован в Moonraker")

    async def _on_print_state_changed(self, web_request, print_info):
        if print_info.get('state') != 'starting':
            return

        filename = print_info.get('filename')
        if not filename:
            return

        file_manager = self.server.lookup_component("file_manager")
        abs_path = os.path.join(file_manager.get_gcode_path(), filename)

        if not os.path.exists(abs_path):
            return

        try:
            self._preprocess_gcode(abs_path)
        except Exception as e:
            logger.error(f"AxisScaler Error: {str(e)}")
            raise ServerError(f"Ошибка препроцессинга усадки осей: {str(e)}")

    def _preprocess_gcode(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 1. Проверяем флаг повторной обработки
        for line in lines[:10]:
            if "pre_scale_preprocessored" in line:
                logger.info(f"AxisScaler: Файл {os.path.basename(file_path)} уже был масштабирован ранее. Пропуск.")
                return

        scale_x, scale_y, scale_z = 1.0, 1.0, 1.0
        params_found = False

        # 2. Ищем параметры масштабирования
        for line in lines[:500]:
            if "pre_scale_x" in line:
                try: scale_x = float(re.search(r'pre_scale_x\s*=\s*([\d.]+)', line).group(1))
                except: pass
                params_found = True
            if "pre_scale_y" in line:
                try: scale_y = float(re.search(r'pre_scale_y\s*=\s*([\d.]+)', line).group(1))
                except: pass
                params_found = True
            if "pre_scale_z" in line:
                try: scale_z = float(re.search(r'pre_scale_z\s*=\s*([\d.]+)', line).group(1))
                except: pass
                params_found = True

        if not params_found or (scale_x == 1.0 and scale_y == 1.0 and scale_z == 1.0):
            logger.info("AxisScaler: Метки масштабирования не найдены. Печать без изменений.")
            return

        logger.info(f"AxisScaler: Начало обработки {os.path.basename(file_path)}. Коэффициенты: X={scale_x}, Y={scale_y}, Z={scale_z}")

        x_re = re.compile(r'([X])([-+]?\d*\.\d+|\d+)')
        y_re = re.compile(r'([Y])([-+]?\d*\.\d+|\d+)')
        z_re = re.compile(r'([Z])([-+]?\d*\.\d+|\d+)')

        new_lines = []
        new_lines.append(f"; pre_scale_preprocessored (X:{scale_x} Y:{scale_y} Z:{scale_z})\n")

        for line in lines:
            if line.strip().startswith(';') or any(cmd in line for cmd in ['M10', 'M14', 'M19']):
                new_lines.append(line)
                continue

            mod_line = line
            if scale_x != 1.0:
                mod_line = x_re.sub(lambda m: f"X{round(float(m.group(2)) * scale_x, 4)}", mod_line)
            if scale_y != 1.0:
                mod_line = y_re.sub(lambda m: f"Y{round(float(m.group(2)) * scale_y, 4)}", mod_line)
            if scale_z != 1.0:
                mod_line = z_re.sub(lambda m: f"Z{round(float(m.group(2)) * scale_z, 4)}", mod_line)

            new_lines.append(mod_line)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        logger.info(f"AxisScaler: Файл {os.path.basename(file_path)} успешно модифицирован и защищен флагом.")

def load_component(config):
    return AxisScaler(config)
