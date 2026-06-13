# Скрипт для кодированиz всего файла в b64

import base64
import sys
import os

def encode_exe_to_base64(input_file, output_file):
    with open(input_file, "rb") as f:
        binary_data = f.read()

    encoded_data = base64.b64encode(binary_data)

    with open(output_file, "wb") as f:
        f.write(encoded_data)

    print(f"Файл '{input_file}' закодирован и сохранён в '{output_file}'")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Использование: python exe_to_b64.py input.exe output.bin")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    encode_exe_to_base64(input_file, output_file)
