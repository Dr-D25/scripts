with open("minimal.exe", "wb") as f:
    f.write(b'MZ')
    f.write(b'\x90\x00')
    f.write(b'\x00' * 58)
    f.write(b'\x40\x00\x00\x00')
    f.write(b'\x00' * (0x40 - 64))