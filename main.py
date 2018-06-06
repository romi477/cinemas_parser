import xml.etree.ElementTree as ET
import os

# xml_file = os.path.curdir + r'\Cinema.xml'
tree = ET.ElementTree(file='Cinema.xml')
owner = tree.find('Owner').attrib['Value']
root = tree.getroot()
title = root.attrib['title']
id = root.attrib['UniqueId']

def write_tree():
    write_tree = ET.ElementTree(file='Statistics.key.original')
    print(write_tree.find('Cinema').attrib['UID'])




def main():
    print(owner)
    print(title)
    print(id)

    write_tree()

if __name__ == '__main__':
    main()