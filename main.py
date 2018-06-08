import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

# xml_file = os.path.curdir + r'\Cinema.xml'
def get_xml():
    lst = []
    tree = ET.ElementTree(file='Cinema.xml')
    owner = tree.find('Owner').attrib['Value']
    root = tree.getroot()
    title = root.attrib['title']
    id = root.attrib['UniqueId']
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
    with open('Stat.xml', 'wb') as f:
        tree.write(f)




def main():

    dic = [{'title': 'RIFTER2.1-CZAKALOV.501-RU', 'id': '3002D4CF-8699-4946-BB02-9414348D9892', 'owner': '11111'},
           {'title': 'RIFTER2.1-CZAKALOV.502-RU', 'id': '23422342-8699-4946-BB02-9414348D9892', 'owner': '22222'}]
    create_xml(dic)

if __name__ == '__main__':
    main()


