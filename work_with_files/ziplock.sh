#!/bin/bash
# архивация файлов папке со случайными паролями.

# исходная директория с файлами.
source_directory="/../../../"

# директория с запароленными файлами. 
destination_directory="/../../../.."

mkdir -p "$destination_directory"

generate_random_password() {
    length=$1
    tr -dc 'A-Za-z0-9' </dev/urandom | head -c ${length:-16}
}

find "$source_directory" -type f -print0 | while IFS= read -r -d '' file; do
    filename=$(basename "$file")
    zipfile="${destination_directory}/${filename%.zip}.zip"
  
    password=$(generate_random_password 12)
   
    zip -P "$password" -j "$zipfile" "$file"

    echo "Архив '$zipfile' создан с паролем: $password"
done