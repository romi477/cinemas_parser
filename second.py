import xml.etree.ElementTree as ET
import os
import sys
import glob


def get_xmls(xml_lst):
    print(sys.getsizeof(xml_lst))
    lst = []
    for i in xml_lst:
        if not i.split('\\')[2].startswith('-'):
            tree = ET.ElementTree(file=i)
            root = tree.getroot()
            title = root.attrib['title']
            uid = root.attrib['UniqueId']
            owner = tree.find('Owner').attrib['Value']
            xml_dic = {'title': title, 'uid': uid, 'owner': owner}
            lst.append(xml_dic)
        else:
            continue
    print(sys.getsizeof(lst))
    return lst

xml_folder = glob.glob(os.path.curdir + r'\!PARSE_cinemas\*\*\Cinema.xml')

print(get_xmls(xml_folder))