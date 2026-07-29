# python vbaparser file 
#.doc, .xls, .ppt

from oletools.olevba import VBA_Parser
import sys

path = sys.argv[1]
vbaparser = VBA_Parser(path)
if vbaparser.detect_vba_macros():
    print('VBA macros found.')

    for (filename, stream_path, vba_filename, vba_code) in vbaparser.extract_macros():
        print('-' * 80)
        print('File Name    :', filename)
        print('OLE stream   :', stream_path)
        print('VBA file     :', vba_filename)
        print('VBA code     :', vba_code)        
else:
    print('Macros not found.')

vbaparser.close()
