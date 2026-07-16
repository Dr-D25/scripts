#!/usr/bin/env python3
# Cкрипт на Python, который работает с любой PE-библиотекой (DLL) и позволяет:

# python search_ordinal_func.py C:\Windows\System32\kernel32.dll
# - вывести все экспортируемые функции с ординалами;

# python search_ordinal_func.py C:\Windows\System32\kernel32.dll -f LoadLibraryA
# - либо найти ординал конкретной функции по имени.


import argparse
import pefile
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Show exported functions and ordinals from a PE DLL"
    )
    parser.add_argument("dll", help="Path to DLL")
    parser.add_argument(
        "-f", "--function",
        help="Function name to search"
    )

    args = parser.parse_args()

    try:
        pe = pefile.PE(args.dll)
    except Exception as e:
        print(f"Cannot open {args.dll}: {e}")
        sys.exit(1)

    if not hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
        print("No export table found.")
        sys.exit(1)

    exports = pe.DIRECTORY_ENTRY_EXPORT.symbols

    if args.function:
        for exp in exports:
            if exp.name and exp.name.decode(errors="ignore") == args.function:
                print(f"{args.function}: ordinal={exp.ordinal}, RVA=0x{exp.address:X}")
                return

        print("Function not found.")
        return

    print(f"{'Ordinal':>7} {'RVA':>10} Name")
    print("-" * 60)

    for exp in exports:
        name = exp.name.decode(errors="ignore") if exp.name else "<ordinal only>"
        print(f"{exp.ordinal:7} 0x{exp.address:08X} {name}")

if __name__ == "__main__":
    main()
