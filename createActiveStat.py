from datetime import datetime
import xml.etree.ElementTree as ET
import os
import glob
import logging

pth = os.path.curdir + r'\logs'
if not os.path.exists(pth):
    os.mkdir(os.path.curdir + r'\logs')
date = datetime.today().strftime("%d-%m-%Y")

logger = logging.getLogger('createActiveStat')
logger.setLevel(logging.DEBUG)

ch1 = logging.StreamHandler()
ch1.setLevel(logging.INFO)
ch2 = logging.FileHandler(filename=os.path.curdir + f'\logs\{date}.log', delay=False)
ch2.setLevel(logging.DEBUG)

formatter1 = logging.Formatter('[%(levelname)s] %(message)s')
formatter2 = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', '%d/%m/%Y %H:%M:%S')

ch1.setFormatter(formatter1)
ch2.setFormatter(formatter2)
logger.addHandler(ch1)
logger.addHandler(ch2)


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
        logger.info(f'Statistics.key.xml for {d["title"]} <{d["uid"][:8]}> was created')
        root.append(cinema)
    logger.debug('--/--')
    tree = ET.ElementTree(root)
    with open('Statistics.key.xml', 'wb') as f:
        tree.write(f)

def create_active(lst):
    root = ET.Element('Activation')
    root.set('UID', f'{lst[0]["uid"]}')
    root.set('Expiration', '2099/01/01')
    logger.info(f'Activation.xml.xml for <{lst[0]["uid"]}> was created')
    logger.debug(f'--/---')
    tree = ET.ElementTree(root)
    with open('Activation.xml.xml', 'wb') as f:
        tree.write(f)


def main():
    xml_folder = glob.glob(os.path.curdir + r'\!PARSE_cinemas\*\*\Cinema.xml')
    xml_file = glob.glob(os.path.curdir + r'\Cinema.xml')
    while True:
        print("""
        1. Create stat-data for all xmls in !PARSE_cinemas
        2. Create stat-data & activation for Cinema.xml in current dir
              """)
        choice = input('your choice: ')
        if choice == '1':
            if xml_folder:
                create_stat(get_xmls(xml_folder))
            else:
                logger.error('there are no xmls in !PARSE_cinemas')
            break
        elif choice == '2':
            if xml_file:
                create_stat(get_xmls(xml_file))
                create_active(get_xmls(xml_file))
            else:
                logger.error('there is no Cinema.xml in current dir')
            break
        else:
            logger.warning('incorrect input, try again')
    input('press Enter to exit...')

if __name__ == '__main__':
    main()

