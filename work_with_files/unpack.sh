#!/bin/bash

TARGET_DIR="${1:-.}"
ARCHIVE_PASSWORD="infected"

cd "$TARGET_DIR" || { echo "Directory not found: $TARGET_DIR"; exit 1; }

for file in *; do
    if [[ -f "$file" ]]; then
        case "$file" in
            *.zip|*.7z|*.rar)
                echo "[+] Extracting $file ..."
                7z x -y -p"$ARCHIVE_PASSWORD" "$file" -o"." || echo "[!] Failed to extract $file"
                ;;
            *.tar)
                tar -xf "$file" || echo "[!] Failed to extract $file" ;;
            *.tar.gz|*.tgz)
                tar -xzf "$file" || echo "[!] Failed to extract $file" ;;
            *.tar.bz2)
                tar -xjf "$file" || echo "[!] Failed to extract $file" ;;
            *)
                echo "Unknown archive format: $file"
                ;;
        esac
    fi
done

echo "Extraction complete (no folders created)."
