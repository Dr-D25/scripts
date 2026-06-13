# python rename_files_in_folder.py /path/to/folder <name_file>

import os
import sys

def rename_files(directory, base_name):
    files = os.listdir(directory)
    count = 1


    for filename in files:
        if os.path.isfile(os.path.join(directory, filename)):
            file_extension = os.path.splitext(filename)[1]
            new_filename = f"{base_name}_{count}{file_extension}"
            old_file = os.path.join(directory, filename)
            new_file = os.path.join(directory, new_filename)

            os.rename(old_file, new_file)
            print(f"Переименован: {filename} -> {new_filename}")
            count += 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    directory_path = sys.argv[1]
    base_name = sys.argv[2]

    rename_files(directory_path, base_name)
