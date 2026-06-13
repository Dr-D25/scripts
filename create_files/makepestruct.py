import struct

def align(val, align_to):
    return (val + align_to - 1) & ~(align_to - 1)

IMAGE_BASE = 0x400000
SECTION_ALIGNMENT = 0x1000
FILE_ALIGNMENT = 0x200
ENTRY_POINT_RVA = 0x1000
SECTION_VA = 0x1000
SECTION_RAW = 0x200

dos_stub = bytearray()
dos_stub += b'MZ'
dos_stub += b'\x90\x00'
dos_stub += b'\x03\x00'
dos_stub += b'\x00\x00'
dos_stub += b'\x04\x00'
dos_stub += b'\x00\x00' * 9
dos_stub += struct.pack('<I', 0x80)
dos_stub += b'\x00' * (0x80 - len(dos_stub))

pe_header = bytearray()
pe_header += b'PE\x00\x00'
pe_header += struct.pack('<H', 0x14c)
pe_header += struct.pack('<H', 1)
pe_header += struct.pack('<I', 0)
pe_header += struct.pack('<I', 0)
pe_header += struct.pack('<I', 0)
pe_header += struct.pack('<H', 0xE0)
pe_header += struct.pack('<H', 0x010F)

opt_header = bytearray()
opt_header += struct.pack('<H', 0x10B)
opt_header += b'\x08\x00'
opt_header += struct.pack('<I', 0x200)
opt_header += struct.pack('<I', 0x200)
opt_header += struct.pack('<I', 0x0)
opt_header += struct.pack('<I', ENTRY_POINT_RVA)
opt_header += struct.pack('<I', SECTION_VA)
opt_header += struct.pack('<I', SECTION_VA)
opt_header += struct.pack('<I', IMAGE_BASE)
opt_header += struct.pack('<I', SECTION_ALIGNMENT)
opt_header += struct.pack('<I', FILE_ALIGNMENT)
opt_header += b'\x04\x00\x00\x00' * 2
opt_header += struct.pack('<I', 0)
opt_header += struct.pack('<I', 0x1000)
opt_header += struct.pack('<I', 0x200)
opt_header += struct.pack('<I', 0x0)
opt_header += struct.pack('<H', 2)
opt_header += struct.pack('<H', 0x140)
opt_header += struct.pack('<I', 0x100000)
opt_header += struct.pack('<I', 0x1000)
opt_header += struct.pack('<I', 0x100000)
opt_header += struct.pack('<I', 0x1000)
opt_header += struct.pack('<I', 0)
opt_header += struct.pack('<I', 16)
opt_header += b'\x00' * (16 * 8)

section_header = bytearray()
section_header += b'.text\x00\x00\x00'
section_header += struct.pack('<I', 0x1000)
section_header += struct.pack('<I', SECTION_VA)
section_header += struct.pack('<I', 0x200)
section_header += struct.pack('<I', SECTION_RAW)
section_header += struct.pack('<I', 0) * 3
section_header += struct.pack('<H', 0) * 2
section_header += struct.pack('<I', 0x60000020)

code = b'\xC3' + b'\x90' * (0x200 - 1)

with open("minimal_ret.exe", "wb") as f:
    f.write(dos_stub)
    f.write(pe_header)
    f.write(opt_header)
    f.write(section_header)
    f.write(code)

print("PE-файл создан: minimal_ret.exe")
