# Скрипт смещает начало файла на 34 байта, оставляя магические байты.
# Делался для проверки кейса - Распаковка измененного zip архива.
# python offset.py file

import os
import sys

file_path = sys.argv[1]

with open(file_path, "rb") as f:
    original_data = f.read()

with open(file_path, "wb") as f:
    f.write(os.urandom(34)) # Указать нужное колическтво байт для сдвига.
    f.write(original_data)
