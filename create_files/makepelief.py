import lief

builder = lief.PE.Binary(lief.PE.PE_TYPE.PE32)
builder.optional_header.addressof_entrypoint = 0x1000
builder.optional_header.imagebase = 0x400000

section = lief.PE.Section(".text")
section.content = [0xC3]
builder.add_section(section)

builder.write("output.exe")
