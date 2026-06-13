# python block_diff.py file1.exe file2.exe -o report.html --json report.json --similarity 0.8 --show common similar


import sys
import os
import argparse
import html
import json
from difflib import SequenceMatcher

import lief
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_MODE_64

SHOW_OPCODES = True
SHOW_ADDRESSES = True
BLOCK_END_MNEMONICS = {
    "ret", "jmp", "call", "retn", "jmpq", "callq",
    "je", "jne", "jz", "jnz", "ja", "jb", "jg", "jl", "jo", "jno",
    "jc", "jnc", "js", "jns", "jnae", "jae", "jnb", "jp", "jnp", 
    "jnbe", "jna", "jbe", "jnle", "jge", "jnl", "jnge", "jle", "jng", "jcxz"
}


def detect_arch(file):
    binary = lief.parse(file)
    if isinstance(binary, lief.PE.Binary):
        m = binary.header.machine
        if m == 0x14c:
            return 'x86'
        elif m == 0x8664:
            return 'x86_64'
    elif isinstance(binary, lief.ELF.Binary):
        m = binary.header.machine
        if m == lief.ELF.ARCH.i386:
            return 'x86'
        elif m == lief.ELF.ARCH.x86_64:
            return 'x86_64'
    elif isinstance(binary, lief.MachO.Binary):
        m = binary.header.cpu_type
        if m == lief.MachO.CPU_TYPES.X86:
            return 'x86'
        elif m == lief.MachO.CPU_TYPES.X86_64:
            return 'x86_64'
    raise Exception("Unsupported or unknown architecture")


def disasm(file, arch):
    binary = lief.parse(file)
    cs = Cs(CS_ARCH_X86, CS_MODE_32 if arch == 'x86' else CS_MODE_64)
    cs.detail = True

    instrs = []
    for sec in binary.sections:
        if sec.size == 0:
            continue
        if isinstance(binary, lief.PE.Binary):
            if sec.characteristics & 0x20000000:
                instrs += list(cs.disasm(bytes(sec.content), sec.virtual_address))
        elif isinstance(binary, lief.ELF.Binary):
            if sec.has(lief.ELF.SECTION_FLAGS.EXECINSTR):
                instrs += list(cs.disasm(bytes(sec.content), sec.virtual_address))
        elif isinstance(binary, lief.MachO.Binary):
            if sec.is_executable:
                instrs += list(cs.disasm(bytes(sec.content), sec.virtual_address))
    return instrs


def split_into_blocks(instrs):
    blocks, current = [], []
    for ins in instrs:
        current.append(ins)
        if ins.mnemonic.lower() in BLOCK_END_MNEMONICS:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def block_signature(block):
    return tuple((i.mnemonic, i.op_str) for i in block)


def format_block(block):
    lines = []
    for i in block:
        addr = f"0x{i.address:x}: " if SHOW_ADDRESSES else ""
        opcodes = f" ; {i.bytes.hex()}" if SHOW_OPCODES else ""
        lines.append(f"{addr}{i.mnemonic:<8} {i.op_str:<30}{opcodes}")
    return "\n".join(lines)


def block_text(block):
    return "\n".join(f"{i.mnemonic} {i.op_str}" for i in block)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def compare_blocks(blocks1, blocks2, similarity_threshold=0.85):
    sigs1 = {block_signature(b): b for b in blocks1}
    sigs2 = {block_signature(b): b for b in blocks2}
    common = set(sigs1) & set(sigs2)

    only1, similar_pairs = [], []
    used_in_2 = set()

    for b1 in blocks1:
        sig1 = block_signature(b1)
        if sig1 in common:
            continue

        best_score, best_idx, best_match = 0, None, None
        for i2, b2 in enumerate(blocks2):
            if i2 in used_in_2 or block_signature(b2) in common:
                continue
            score = similar(block_text(b1), block_text(b2))
            if score > best_score:
                best_score, best_idx, best_match = score, i2, b2

        if best_score >= similarity_threshold and best_match:
            similar_pairs.append((b1, best_match, best_score))
            used_in_2.add(best_idx)
        else:
            only1.append(b1)

    only2_final = [b for i, b in enumerate(blocks2) if i not in used_in_2 and block_signature(b) not in common]

    return {
        "common": [sigs1[k] for k in common],
        "only_in_1": only1,
        "only_in_2": only2_final,
        "similar": similar_pairs
    }


def write_html_report(results, file1, file2, output_path="comparison_report.html", show_types=None):
    if show_types is None:
        show_types = {"common", "only_in_1", "only_in_2", "similar"}

    html_parts = [
        "<html><head><meta charset='utf-8'><style>",
        "body { font-family: monospace; background: #f8f8f8; color: #111; }",
        "pre { background: #fff; padding: 1em; border: 1px solid #ccc; margin-bottom: 1em; overflow-x:auto; }",
        "h2 { border-bottom: 1px solid #ccc; padding-bottom: 0.2em; }",
        "</style></head><body>",
        f"<h1>Comparison Report: {html.escape(file1)} vs {html.escape(file2)}</h1>"
    ]

    def block_html(title, blocks, color="#e8f8e8"):
        html_blocks = [f"<h2>{title}</h2>"]
        for i, block in enumerate(blocks):
            html_blocks.append(f"<pre style='background:{color};'><b>Block {i}</b>\n{html.escape(format_block(block))}</pre>")
        return "\n".join(html_blocks)

    def similar_block_html(pairs):
        html_blocks = ["<h2>Similar Blocks</h2>"]
        for i, (b1, b2, score) in enumerate(pairs):
            html_blocks.append(
                f"<pre style='background:#fff8e8;'><b>Pair {i} (similarity: {score:.2f})</b>\n"
                f"<u>Block from {html.escape(file1)}</u>:\n{html.escape(format_block(b1))}\n\n"
                f"<u>Block from {html.escape(file2)}</u>:\n{html.escape(format_block(b2))}</pre>"
            )
        return "\n".join(html_blocks)

    if 'common' in show_types:
        html_parts.append(block_html("Matching Blocks", results["common"]))
    if 'only_in_1' in show_types:
        html_parts.append(block_html(f"Unique Blocks in {file1}", results["only_in_1"], "#fbeaea"))
    if 'only_in_2' in show_types:
        html_parts.append(block_html(f"Unique Blocks in {file2}", results["only_in_2"], "#eaf3fb"))
    if 'similar' in show_types:
        html_parts.append(similar_block_html(results["similar"]))

    html_parts.append("</body></html>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(html_parts))
    print(f"[+] HTML report saved to: {output_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare two binaries on block level and generate reports")
    parser.add_argument("file1")
    parser.add_argument("file2")
    parser.add_argument("-o", "--out", default="comparison_report.html", help="HTML report path")
    parser.add_argument("--json", help="JSON report path")
    parser.add_argument("--similarity", type=float, default=0.85, help="similarity threshold")
    parser.add_argument("--show", nargs='+', choices=["common", "only_in_1", "only_in_2", "similar"], default=["common", "only_in_1", "only_in_2", "similar"], help="Types of blocks to include in HTML report")
    args = parser.parse_args(argv)

    arch = detect_arch(args.file1)
    print(f"[+] Architecture detected: {arch}")

    instrs1 = disasm(args.file1, arch)
    instrs2 = disasm(args.file2, arch)

    blocks1 = split_into_blocks(instrs1)
    blocks2 = split_into_blocks(instrs2)

    print(f"[+] Blocks: file1 = {len(blocks1)}, file2 = {len(blocks2)}")

    results = compare_blocks(blocks1, blocks2, similarity_threshold=args.similarity)

    print(f"[=] Matching blocks: {len(results['common'])}")
    print(f"[+] Unique in {args.file1}: {len(results['only_in_1'])}")
    print(f"[+] Unique in {args.file2}: {len(results['only_in_2'])}")
    print(f"[~] Similar blocks: {len(results['similar'])}")

    write_html_report(results, args.file1, args.file2, output_path=args.out, show_types=set(args.show))
    if args.json:
        write_json_report(results, args.file1, args.file2, output_path=args.json)

if __name__ == "__main__":
    main()
