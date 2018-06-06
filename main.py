import xml.etree.ElementTree as ET
import os

# xml_file = os.path.curdir + r'\Cinema.xml'
tree = ET.ElementTree(file='Cinema.xml')
owner = tree.find('Owner').attrib['Value']
root = tree.getroot()
title = root.attrib['title']
id = root.attrib['UniqueId']

def write_tree(UID, title, owner):
    write_tree = ET.ElementTree(file='Statistics.key.original')
    arg = write_tree.find('Cinema').attrib
    arg['UID'] = UID
    arg['Name'] = title + '-' + owner
    # print(arg['UID'])
    # print(arg['Name'])
    print(arg)
    tree = ET.ElementTree(write_tree)
    with open('myxml.xml', 'w') as f:
        tree.write(f)


def main():
    print(owner)
    print(title)
    print(id)
    print('*' * 10)
    write_tree(id, title, owner)

if __name__ == '__main__':
    main()


