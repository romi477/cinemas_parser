import xml.etree.ElementTree as ET
import os
import glob
import logging


def get_xmls(xml_lst):
    lst = []
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

def create_active(lst):
    root = ET.Element('Activation')
    root.set('UID', f'{lst[0]["uid"]}')
    root.set('Expiration', '2099/01/01')
    tree = ET.ElementTree(root)
    with open('Activation.xml.xml', 'wb') as f:
        tree.write(f)


def main():
    while True:
        print("""
        1. Create stat-data for all xmls from \!PARSE_cinemas
        2. Create stat-data & activation for xml in current dir
              """)
        xml_folder = glob.glob(os.path.curdir + r'\!PARSE_cinemas\*\*\Cinema.xml')
        xml_file = glob.glob(os.path.curdir + r'\Cinema.xml')
        choice = input('your choice: ')
        if choice == '1':
            create_stat(get_xmls(xml_folder))
            print('stat-data successfully created...')
            break
        elif choice == '2':
            create_stat(get_xmls(xml_file))
            create_active(get_xmls(xml_file))
            print('stat-data % activation successfully created...')
            break
        else:
            print('incorrect input, try again...')
    input('press Enter to exit...')

if __name__ == '__main__':
    main()

