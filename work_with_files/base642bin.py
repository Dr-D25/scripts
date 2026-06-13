# Используется для декодирования из base64 и записи в файл.
import base64
import sys
import os

def main():
    if len(sys.argv) < 2:
        print("Использование: python decode_base64.py <имя_файла>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.isfile(input_file):
        print(f"Ошибка: файл '{input_file}' не найден.")
        sys.exit(1)

    output_file = os.path.splitext(input_file)[0] + "_decoded.bin"

    with open(input_file, "r", encoding="utf-8") as f:
        base64_data = "".join(f.read().split())

    try:
        binary_data = base64.b64decode(base64_data)
    except Exception as e:
        print(f"Ошибка при декодировании: {e}")
        sys.exit(1)

    with open(output_file, "wb") as f:
        f.write(binary_data)

    print(f"Файл успешно декодирован и сохранён как '{output_file}'")

if __name__ == "__main__":
    main()
