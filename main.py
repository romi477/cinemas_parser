import xml.etree.ElementTree as ET
import os
import glob

def get_xmls():
    lst = []
    xml_lst  = glob.glob(os.path.curdir + r'\PARSE_cinemas\*\*\Cinema.xml')
    for i in xml_lst:
        tree = ET.ElementTree(file=i)
        root = tree.getroot()
        title = root.attrib['title']
        id = root.attrib['UniqueId']
        owner = tree.find('Owner').attrib['Value']
        xml_dic = {'title': title, 'id': id, 'owner': owner}
        lst.append(xml_dic)
    return lst

def create_xml(lst):
    root = ET.Element('StatisticsExportKey')
    for d in lst:
        cinema = ET.Element('Cinema')
        cinema.set('Name', f'{d["title"]}-{d["owner"]}')
        cinema.set('UID', f'{d["id"]}')
        root.append(cinema)
    tree = ET.ElementTree(root)
    with open('Statistics.key.xml', 'wb') as f:
        tree.write(f)

def main():
    create_xml(get_xmls())

if __name__ == '__main__':
    main()


