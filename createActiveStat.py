import xml.etree.ElementTree as ET
import os
import glob

def get_xmls():
    lst = []
    xml_lst  = glob.glob(os.path.curdir + r'\!PARSE_cinemas\*\*\Cinema.xml')
    for i in xml_lst:
        tree = ET.ElementTree(file=i)
        root = tree.getroot()
        title = root.attrib['title']
        uid = root.attrib['UniqueId']
        owner = tree.find('Owner').attrib['Value']
        xml_dic = {'title': title, 'uid': uid, 'owner': owner}
        lst.append(xml_dic)
    return lst

def create_stat(lst):
    root = ET.Element('StatisticsExportKey')
    for d in lst:
        cinema = ET.Element('Cinema')
        cinema.set('Name', f'{d["title"]}-{d["owner"]}')
        cinema.set('UID', f'{d["uid"]}')
        root.append(cinema)
    tree = ET.ElementTree(root)
    with open('Statistics.key.xml', 'wb') as f:
        tree.write(f)

def create_active():
    root = ET.Element('Activation')
    root.set('UID', 'qwerty')
    root.set('Expiration', '2099/01/01')

    tree = ET.ElementTree(root)
    with open('Activation.xml.xml', 'wb') as f:
        tree.write(f)


def main():
    pass
    # create_stat(get_xmls())
    create_active()
if __name__ == '__main__':

    main()

