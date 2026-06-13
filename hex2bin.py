# Скрипт для преобразования HEX строки в исполняемый файл.


import sys

if len(sys.argv) != 3:
    print(f"Использование: python {sys.argv[0]} text_file_name exec_file_name")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(input_file, "r") as f:
    hex_string = f.read().strip()

binary_data = bytes.fromhex(hex_string)

with open(output_file, "wb") as f:
    f.write(binary_data)

print(f"Файл успешно создан: {output_file}")