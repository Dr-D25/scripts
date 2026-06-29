#!/usr/bin/env python3
# Создание базы
# python cve_json_pars.py --init ~/path/to/dir

# Сравнение с базой
# python cve_json_pars.py ~/path/to/dir

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

DATABASE_FILE = "cve_database.json"
LOG_FILE = "changes.log"


def load_database():
    db_path = Path(DATABASE_FILE)

    if not db_path.exists():
        return {}

    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_database(database):
    result = {}

    for module in sorted(database.keys()):
        result[module] = sorted(database[module])

    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)




def parse_json_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    modules = {}

    for item in data:

        pkg = item.get("pkg")
        vulns = item.get("vulnerabilities", [])

        if not pkg:
            continue

        if pkg not in modules:
            modules[pkg] = set()

        modules[pkg].update(vulns)

    return modules



def scan_directory(directory):
    result = {}

    json_files = sorted(Path(directory).glob("*.json"))

    if not json_files:
        print("JSON files not found.")
        return result

    for file in json_files:

        print(f"Scanning {file.name}")

        try:
            modules = parse_json_file(file)

            for pkg, cves in modules.items():

                if pkg not in result:
                    result[pkg] = set()

                result[pkg].update(cves)

        except Exception as e:
            print(f"ERROR: {file.name}: {e}")

    return result




def initialize_database(directory):

    print("\nInitializing database...\n")

    modules = scan_directory(directory)

    save_database(modules)

    total_cves = sum(len(v) for v in modules.values())

    print("\nDatabase created.\n")
    print(f"Modules : {len(modules)}")
    print(f"Unique CVE : {total_cves}")



def append_log(lines):

    if not lines:
        return

    with open(LOG_FILE, "a", encoding="utf-8") as f:

        f.write("=" * 70 + "\n")
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.write("\n")
        f.write("=" * 70 + "\n\n")

        for line in lines:
            f.write(line + "\n")

        f.write("\n")




def compare(directory):

    database = load_database()

    if not database:
        print("Database not found.")
        print("Run:")
        print("    python script.py --init <directory>")
        return

    database = {
        k: set(v)
        for k, v in database.items()
    }

    scanned = scan_directory(directory)

    new_modules = 0
    new_cves = 0

    log = []

    print("\n")

    for module in sorted(scanned.keys()):

        if module not in database:

            new_modules += 1

            database[module] = scanned[module]

            print("=" * 60)
            print("NEW MODULE")
            print("=" * 60)
            print(module)

            log.append(f"NEW MODULE: {module}")

            for cve in sorted(scanned[module]):
                print("   ", cve)
                log.append(f"    {cve}")

            log.append("")

            continue

        diff = scanned[module] - database[module]

        if diff:

            new_cves += len(diff)

            print("=" * 60)
            print("NEW CVE")
            print("=" * 60)
            print(module)

            log.append(f"NEW CVE: {module}")

            for cve in sorted(diff):
                print("   +", cve)
                log.append(f"    + {cve}")

            log.append("")

            database[module].update(diff)

    save_database(database)

    append_log(log)

    print("\n")
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Modules in database : {len(database)}")
    print(f"New modules         : {new_modules}")
    print(f"New CVE             : {new_cves}")

    if new_modules == 0 and new_cves == 0:
        print("\nDatabase already up-to-date.")



def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--init",
        action="store_true",
        help="Create new database"
    )

    parser.add_argument(
        "directory",
        help="Directory with JSON files"
    )

    args = parser.parse_args()

    if not Path(args.directory).exists():
        print("Directory not found.")
        sys.exit(1)

    if args.init:
        initialize_database(args.directory)
    else:
        compare(args.directory)


if __name__ == "__main__":
    main()
