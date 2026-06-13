#python sorted_magic_bytes.py
import os
import shutil

def move_files_with_header(source_folder, target_folder, header_bytes):
    os.makedirs(target_folder, exist_ok=True)

    for filename in os.listdir(source_folder):
        file_path = os.path.join(source_folder, filename)

        if os.path.isfile(file_path):
            with open(file_path, 'rb') as file:
                header = file.read(len(header_bytes))
                if header == header_bytes:
                    shutil.move(file_path, os.path.join(target_folder, filename))
                    print(f'Файл {filename} перемещен в папку {target_folder}.')

    print('Проверка завершена.')

if __name__ == "__main__":
    header_input = input("Введите байты для поиска (например, MZ): ")
    source_folder = input("Введите путь до папки с файлами: ")
    target_folder = input("Введите название папки для перемещения файлов: ")

    header_bytes = header_input.encode('utf-8')

    target_folder_path = os.path.join(source_folder, target_folder)

    move_files_with_header(source_folder, target_folder_path, header_bytes)

