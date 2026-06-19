#!/usr/bin/env python3
"""
ssdeep_compare.py - поиск похожих файлов по нечётким хэшам ssdeep
с поддержкой кластеризации и подсветки совпадающих блоков.
"""

import os
import sys
import argparse
import csv
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor, as_completed

import ppdeep

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    class Fore:
        GREEN = ''
        RESET = ''
    class Style:
        BRIGHT = ''
        RESET_ALL = ''


def compute_hash(filepath):
    try:
        h = ppdeep.hash_from_file(filepath)
        return (filepath, h)
    except Exception as e:
        print(f"Ошибка при хэшировании {filepath}: {e}", file=sys.stderr)
        return (filepath, None)


def get_files(paths, recursive):
    files = []
    for p in paths:
        if os.path.isfile(p):
            files.append(p)
        elif os.path.isdir(p) and recursive:
            for root, _, filenames in os.walk(p):
                for f in filenames:
                    files.append(os.path.join(root, f))
        elif os.path.isdir(p) and not recursive:
            print(f"Пропускаем каталог {p} (используйте -r для рекурсивного обхода)", file=sys.stderr)
    return files


def compare_pair(h1, h2):
    return ppdeep.compare(h1, h2)


def highlight_blocks(block1, block2):
    
    if not HAS_COLORAMA:
        return block1, block2

    max_len = max(len(block1), len(block2))
    b1 = block1.ljust(max_len)
    b2 = block2.ljust(max_len)

    colored1 = []
    colored2 = []
    for ch1, ch2 in zip(b1, b2):
        if ch1 == ch2 and ch1 != ' ':
            colored1.append(Fore.GREEN + Style.BRIGHT + ch1 + Fore.RESET)
            colored2.append(Fore.GREEN + Style.BRIGHT + ch2 + Fore.RESET)
        else:
            colored1.append(ch1)
            colored2.append(ch2)
    return ''.join(colored1), ''.join(colored2)


def find_clusters(file_list, hash_map, threshold):
    
    n = len(file_list)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    for i in range(n):
        for j in range(i+1, n):
            h1 = hash_map[file_list[i]]
            h2 = hash_map[file_list[j]]
            if ppdeep.compare(h1, h2) >= threshold:
                union(i, j)

    clusters_dict = {}
    for i, f in enumerate(file_list):
        root = find(i)
        clusters_dict.setdefault(root, []).append(f)

    clusters = [sorted(clist) for clist in clusters_dict.values() if len(clist) >= 2]
    return clusters


def main():
    parser = argparse.ArgumentParser(description="Поиск похожих файлов по ssdeep хэшам")
    parser.add_argument('paths', nargs='+', help="Файлы или каталоги для анализа")
    parser.add_argument('-r', '--recursive', action='store_true', help="Рекурсивно обходить каталоги")
    parser.add_argument('-t', '--threshold', type=int, default=50,
                        help="Порог схожести (0-100), выше которого выводятся пары (по умолчанию 50)")
    parser.add_argument('-s', '--show-hashes', action='store_true', help="Показывать полные хэши для каждой пары/кластера")
    parser.add_argument('-b', '--show-blocks', action='store_true', help="Показывать совпадающие блоки хэшей (подробно)")
    parser.add_argument('-o', '--output', choices=['text', 'csv'], default='text',
                        help="Формат вывода: text (таблица) или csv (по умолчанию text)")
    parser.add_argument('-j', '--jobs', type=int, default=4, help="Количество потоков для хэширования (по умолчанию 4)")
    
    parser.add_argument('--list-hashes', action='store_true',
                        help="Вывести список всех файлов с их хэшами и завершить работу (без сравнения)")
    parser.add_argument('--output-hashes', type=str,
                        help="Сохранить список хэшей в указанный файл (работает только с --list-hashes)")
    parser.add_argument('--cluster', action='store_true',
                        help="Группировать файлы в кластеры (вместо попарного вывода)")
    parser.add_argument('--highlight', action='store_true',
                        help="Подсвечивать совпадающие участки в блоках хэшей (для попарного вывода или внутри кластеров)")
    parser.add_argument('--min-cluster-size', type=int, default=2,
                        help="Минимальный размер кластера для отображения (по умолчанию 2)")

    args = parser.parse_args()

    files = get_files(args.paths, args.recursive)
    if not files:
        print("Нет файлов для обработки.", file=sys.stderr)
        sys.exit(1)

    print(f"Найдено файлов: {len(files)}. Вычисление хэшей...", file=sys.stderr)

    hash_map = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        future_to_file = {executor.submit(compute_hash, f): f for f in files}
        for future in as_completed(future_to_file):
            fpath, h = future.result()
            if h is not None:
                hash_map[fpath] = h

    if not hash_map:
        print("Не удалось вычислить ни одного хэша.", file=sys.stderr)
        sys.exit(1)

    if args.list_hashes:
        out_stream = open(args.output_hashes, 'w') if args.output_hashes else sys.stdout
        try:
            for fpath, h in sorted(hash_map.items()):
                out_stream.write(f"{fpath}: {h}\n")
        finally:
            if args.output_hashes:
                out_stream.close()
        print(f"Список хэшей сохранён в {args.output_hashes}" if args.output_hashes else "", file=sys.stderr)
        sys.exit(0)

    if len(hash_map) < 2:
        print("Недостаточно файлов с успешно вычисленными хэшами для сравнения (нужно как минимум 2).", file=sys.stderr)
        sys.exit(1)

    file_list = list(hash_map.keys())

    if args.cluster:
        clusters = find_clusters(file_list, hash_map, args.threshold)
        clusters = [c for c in clusters if len(c) >= args.min_cluster_size]
        if not clusters:
            print(f"Не найдено кластеров с размером >= {args.min_cluster_size} и схожестью >= {args.threshold}%.")
            sys.exit(0)

        print(f"\nНайдено кластеров: {len(clusters)}")
        for idx, cluster in enumerate(clusters, 1):
            print(f"\n=== Кластер #{idx} (размер {len(cluster)}) ===")
            if args.show_hashes:
                if args.highlight:
                    print("  Попарное сравнение внутри кластера (с подсветкой):")
                    for i in range(len(cluster)):
                        for j in range(i+1, len(cluster)):
                            f1, f2 = cluster[i], cluster[j]
                            h1, h2 = hash_map[f1], hash_map[f2]
                            score = ppdeep.compare(h1, h2)
                            if score >= args.threshold:
                                print(f"    {f1} <-> {f2}  [схожесть {score}%]")
                                if args.show_blocks:
                                    parts1 = h1.split(':')
                                    parts2 = h2.split(':')
                                    if len(parts1) >= 3 and len(parts2) >= 3:
                                        block1, block2 = parts1[1], parts2[1]
                                        c1, c2 = highlight_blocks(block1, block2)
                                        print(f"      Блок1: {c1}")
                                        print(f"      Блок2: {c2}")
                else:
                    for f in cluster:
                        print(f"  {f}: {hash_map[f]}")
            else:
                for f in cluster:
                    print(f"  {f}")
        sys.exit(0)

    print(f"Успешно вычислено хэшей: {len(hash_map)}. Сравнение...", file=sys.stderr)
    results = []
    total_pairs = len(file_list) * (len(file_list) - 1) // 2
    processed = 0
    for i, j in combinations(range(len(file_list)), 2):
        f1 = file_list[i]
        f2 = file_list[j]
        h1 = hash_map[f1]
        h2 = hash_map[f2]
        score = ppdeep.compare(h1, h2)
        if score >= args.threshold:
            results.append((f1, f2, score, h1, h2))
        processed += 1
        if processed % 100 == 0:
            print(f"  Обработано пар: {processed}/{total_pairs}", file=sys.stderr)

    results.sort(key=lambda x: x[2], reverse=True)

    
    if args.output == 'csv':
        writer = csv.writer(sys.stdout)
        writer.writerow(['file1', 'file2', 'similarity', 'hash1', 'hash2'])
        for f1, f2, score, h1, h2 in results:
            writer.writerow([f1, f2, score, h1, h2])
    else:
        if not results:
            print(f"Не найдено пар со схожестью >= {args.threshold}%.")
            sys.exit(0)

        max_len1 = max(len(f) for f, _, _, _, _ in results)
        max_len2 = max(len(f) for _, f, _, _, _ in results)
        header = f"{'Файл 1'.ljust(max_len1)}  {'Файл 2'.ljust(max_len2)}  Схожесть"
        print(header)
        print('-' * len(header))
        for f1, f2, score, h1, h2 in results:
            print(f"{f1.ljust(max_len1)}  {f2.ljust(max_len2)}  {score:3d}%")
            if args.show_hashes:
                print(f"  Хэш1: {h1}")
                print(f"  Хэш2: {h2}")
                if args.show_blocks:
                    parts1 = h1.split(':')
                    parts2 = h2.split(':')
                    if len(parts1) >= 3 and len(parts2) >= 3:
                        block1, block2 = parts1[1], parts2[1]
                        if args.highlight:
                            c1, c2 = highlight_blocks(block1, block2)
                            print(f"  Блок1: {c1}")
                            print(f"  Блок2: {c2}")
                        else:
                            print(f"  Блок1: {block1}")
                            print(f"  Блок2: {block2}")
                    else:
                        print("  (не удалось разобрать блоки)")
            print()

    print(f"\nНайдено пар с совпадением >= {args.threshold}%: {len(results)}", file=sys.stderr)


if __name__ == '__main__':
    main()
