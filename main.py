import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

# xml_file = os.path.curdir + r'\Cinema.xml'
def get_xml():
    tree = ET.ElementTree(file='Cinema.xml')
    owner = tree.find('Owner').attrib['Value']
    root = tree.getroot()
    title = root.attrib['title']
    id = root.attrib['UniqueId']
    xml_dic = {'title': title, 'id': id, 'owner': owner}
    return xml_dic

def create_xml():
    doc = minidom.Document()
    root = doc.createElement('StatisticsExportKey')
    doc.appendChild(root)
    xml_str = doc.toprettyxml(indent='  ')
    with open('Statistics.key', 'a') as f:
        f.write(xml_str)

def write_xml(dic):
    dom = minidom.parse('Statistics2.key')
    dom.normalize()
    cinema = dom.createElement('Cinema')
    # cinema.setAttribute('UID', f'{dic["id"]}')
    # cinema.setAttribute('Name', f'{dic["title"]}-{dic["owner"]}')
    dom.appendChild(cinema)
    cinema_data = dom.toprettyxml(indent='  ')
    with open('Statistics2.key', 'a') as f:
        f.write(cinema_data)





def main():
    # create_xml()
    write_xml(get_xml())

if __name__ == '__main__':
    main()


