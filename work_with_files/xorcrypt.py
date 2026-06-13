import argparse

def xor_file(inp_file, out_file, key=0x13):
    with open(inp_file, 'rb') as infile, open(out_file, 'wb') as outfile:
        byte = infile.read(1)

        while byte:
            if byte[0] == 0x00:
                outfile.write(byte)
            else:
                outfile.write(bytes([byte[0] ^ key]))
            byte = infile.read(1)


if __name__ == '__main__':
    pars = argparse.ArgumentParser(description='XOR each byte of a file with a given key')
    pars.add_argument('inp_file', type=str, help='Input file to be processed')
    pars.add_argument('-o', '--out_file', type=str, required=True, help='Output file to save the result')
    args = pars.parse_args()
    xor_file(args.inp_file, args.out_file)