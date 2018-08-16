import glob
import os
from pathlib import Path


# xml_folder = glob.glob(os.path.curdir + r'\!PARSE_cinemas\*', recursive=False)
# xml_folder2 = os.walk(r'!PARSE_cinemas')
#
# for i in xml_folder2:
#     print(i)
# print(xml_folder)

p = Path('!PARSE_cinemas')

for i in p.iterdir():
    print(i)