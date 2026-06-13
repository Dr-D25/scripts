import pefile
import sys

def calculate_imphash(file_path):
    try:
        pe = pefile.PE(file_path)
        imphash = pe.get_imphash()
        return imphash
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python imphash.py <путь_к_exe_файлу>")
        sys.exit(1)

    exe_file_path = sys.argv[1]
    imphash = calculate_imphash(exe_file_path)

    if imphash:
        print(f"Imphash {exe_file_path}: {imphash}")

