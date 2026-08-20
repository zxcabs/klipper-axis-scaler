#klipper-axis-scaler

## Install
- Clone repo and run `install.sh`
- Add to printer.cfg
```
[gcode_shell_command preprocess_axes]
command: python3 /home/mks/printer_data/config/axis_scaler.py
timeout: 10.0
verbose: True
```
- Add to PRINT_START
```
    {% set current_gcode_file = printer.virtual_sdcard.file_path %}
    
    {action_respond_info("Запуск препроцессора усадки для активного файла...")}
    RUN_SHELL_COMMAND CMD=preprocess_axes PARAMS="\"{current_gcode_file}\""
```
- Probably you shuld install klipper plugin `Gcode Shell Command` wia `KIAUH`
