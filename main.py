import xml.etree.ElementTree as ET
import os

# xml_file = os.path.curdir + r'\Cinema.xml'
tree = ET.ElementTree(file='Cinema.xml')
# print(tree.getroot())
root = tree.getroot()
print(root.tag)
print(root.attrib)

iter_tree = root.getiterator()
for i in iter_tree:
    print(f'{i.tag} = {i.text}')

print('*' * 20)

childrens = root.getchildren()
for j in childrens:
    # for k in j.getchildren():
    print(f'{j.tag} = {j.text}')



