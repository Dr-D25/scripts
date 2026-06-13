import struct
import os

def align(val, align_to):
    return (val + align_to - 1) & ~(align_to - 1)

IMAGE_BASE = 0x400000
SECTION_ALIGNMENT = 0x1000
FILE_ALIGNMENT = 0x200

text_section_va = 0x1000
text_section_raw = 0x200
text_section_size = 0x200

junk_section_va = align(text_section_va + text_section_size, SECTION_ALIGNMENT)
junk_section_raw = align(text_section_raw + text_section_size, FILE_ALIGNMENT)
junk_section_size = 0x200

entry_point_rva = text_section_va

dos_stub = bytearray()
dos_stub += b'MZ' + b'\x90\x00' + b'\x03\x00' + b'\x00\x00' + b'\x04\x00'
dos_stub += b'\x00\x00' * 9
dos_stub += struct.pack('<I', 0x80)
dos_stub += b'\x00' * (0x80 - len(dos_stub))

pe_header = bytearray()
pe_header += b'PE\x00\x00'
pe_header += struct.pack('<H', 0x14c)
pe_header += struct.pack('<H', 2)
pe_header += struct.pack('<I', 0)
pe_header += struct.pack('<I', 0)
pe_header += struct.pack('<I', 0)
pe_header += struct.pack('<H', 0xE0)
pe_header += struct.pack('<H', 0x010F)

opt_header = bytearray()
opt_header += struct.pack('<H', 0x10B)
opt_header += b'\x08\x00'
opt_header += struct.pack('<I', text_section_size)
opt_header += struct.pack('<I', junk_section_size)
opt_header += struct.pack('<I', 0)
opt_header += struct.pack('<I', entry_point_rva)
opt_header += struct.pack('<I', text_section_va)
opt_header += struct.pack('<I', junk_section_va)
opt_header += struct.pack('<I', IMAGE_BASE)
opt_header += struct.pack('<I', SECTION_ALIGNMENT)
opt_header += struct.pack('<I', FILE_ALIGNMENT)
opt_header += struct.pack('<I', 0) * 2
opt_header += struct.pack('<I', 0)
opt_header += struct.pack('<I', junk_section_va + junk_section_size)
opt_header += struct.pack('<I', 0x200)
opt_header += struct.pack('<I', 0)
opt_header += struct.pack('<H', 2)
opt_header += struct.pack('<H', 0x140)
opt_header += struct.pack('<I', 0x100000)
opt_header += struct.pack('<I', 0x1000)
opt_header += struct.pack('<I', 0x100000)
opt_header += struct.pack('<I', 0x1000)
opt_header += struct.pack('<I', 0)
opt_header += struct.pack('<I', 16)
opt_header += b'\x00' * (16 * 8)

section_headers = bytearray()

section_headers += b'.text\x00\x00\x00'
section_headers += struct.pack('<I', text_section_size)
section_headers += struct.pack('<I', text_section_va)
section_headers += struct.pack('<I', text_section_size)
section_headers += struct.pack('<I', text_section_raw)
section_headers += struct.pack('<I', 0) * 3
section_headers += struct.pack('<H', 0) * 2
section_headers += struct.pack('<I', 0x60000020)


section_headers += b'.junk\x00\x00\x00'
section_headers += struct.pack('<I', junk_section_size)
section_headers += struct.pack('<I', junk_section_va)
section_headers += struct.pack('<I', junk_section_size)
section_headers += struct.pack('<I', junk_section_raw)
section_headers += struct.pack('<I', 0) * 3
section_headers += struct.pack('<H', 0) * 2
section_headers += struct.pack('<I', 0x40000040)

text_code = b'\xC3' + b'\x90' * (text_section_size - 1)

def xor_encrypt(data: bytes, key: int) -> bytes:
    return bytes(b ^ key for b in data)

payload = b'SecretMessage:Dr-D25'
key = 0xAA
encrypted_payload = xor_encrypt(payload.ljust(junk_section_size, b'\x00'), key)

with open("pe_with_junk.exe", "wb") as f:
    f.write(dos_stub)
    f.write(pe_header)
    f.write(opt_header)
    f.write(section_headers)

    f.write(b'\x00' * (text_section_raw - f.tell()))
    f.write(text_code)

    f.write(b'\x00' * (junk_section_raw - f.tell()))
    f.write(encrypted_payload)

print("PE с ложной секцией создан: pe_with_junk.exe")
print("Вшитый зашифрованный payload:", payload)



# Decrypt SecretMessage

# BYTE* junk = GetModuleHandle(NULL) + 0x2000;
# for (int i = 0; i < 32; ++i) {
#     printf("%c", junk[i] ^ 0xAA);
# }