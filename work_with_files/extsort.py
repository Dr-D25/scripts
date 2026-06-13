#python sorted_ext.py /path/to/dir
import os
import shutil
import sys

def organize_files_by_extension(source_folder):

    if not os.path.exists(source_folder):
        print(f"Directory '{source_folder}' not found.")
        return


    for filename in os.listdir(source_folder):

        file_path = os.path.join(source_folder, filename)
        

        if os.path.isfile(file_path):

            file_extension = filename.split('.')[-1] if '.' in filename else 'no_extension'
            
            extension_folder = os.path.join(source_folder, file_extension)
            os.makedirs(extension_folder, exist_ok=True)
            

            shutil.move(file_path, os.path.join(extension_folder, filename))

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("error arguments")
    else:
        source_folder = sys.argv[1]
        organize_files_by_extension(source_folder)
