from datetime import datetime
import xml.etree.ElementTree as ET
import os
import glob
import logging

date = datetime.today()
pth = os.path.curdir + f'\logs\{date.strftime("%m-%Y")}'
if not os.path.exists(pth):
    os.mkdir(os.path.curdir + f'\logs\{date.strftime("%m-%Y")}')

logger = logging.getLogger('createActiveStat')
logger.setLevel(logging.DEBUG)

ch1 = logging.StreamHandler()
ch1.setLevel(logging.INFO)
ch2 = logging.FileHandler(filename=pth + f'\{date.strftime("%d-%m-%Y")}.log', delay=False)
ch2.setLevel(logging.DEBUG)

formatter1 = logging.Formatter('[%(levelname)s] %(message)s')
formatter2 = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', '%d/%m/%Y %H:%M:%S')

ch1.setFormatter(formatter1)
ch2.setFormatter(formatter2)
logger.addHandler(ch1)
logger.addHandler(ch2)

def getLst_i(i):
    tree = ET.ElementTree(file=i)
    root = tree.getroot()
    title = root.attrib['title']
    uid = root.attrib['UniqueId']
    owner = tree.find('Owner').attrib['Value']
    return {'title': title, 'uid': uid, 'owner': owner}

def get_xmls(xml_lst):
    lst = []
    lstExclude = []
    for i in xml_lst:
        try:
            nameDir = i.split('\\')[2]
            if not nameDir.startswith('-'):
                lst.append(getLst_i(i))
            else:
                if nameDir not in lstExclude:
                    lstExclude.append(nameDir)
                    logger.debug(f'directory {nameDir[1:]} was skipped')
                continue
        except IndexError:
            lst.append(getLst_i(i))
    return lst

def create_stat(lst):
    root = ET.Element('StatisticsExportKey')
    for d in lst:
        cinema = ET.Element('Cinema')
        cinema.set('Name', f'{d["title"]}-{d["owner"]}')
        cinema.set('UID', f'{d["uid"]}')
        logger.info(f'Statistics.key.xml for {d["title"]} <{d["uid"]}> was created')
        root.append(cinema)
    tree = ET.ElementTree(root)
    with open('Statistics.key.xml', 'wb') as f:
        tree.write(f)

def create_active(lst):
    root = ET.Element('Activation')
    root.set('UID', f'{lst[0]["uid"]}')
    root.set('Expiration', '2099/01/01')
    logger.info(f'Activation.xml.xml for <{lst[0]["uid"]}> was created')
    tree = ET.ElementTree(root)
    with open('Activation.xml.xml', 'wb') as f:
        tree.write(f)


def main():
    logger.debug('-- beginning of log --')
    filesForDelete = ['Activation.xml.xml', 'Activation.xml', 'Statistics.key.xml', 'Statistics.key']
    for file in filesForDelete:
        try:
            os.remove(file)
            logger.debug(f'{file} was removed')
        except FileNotFoundError:
            logger.debug(f"{file} was't found" )
            pass

    xml_folder = glob.glob(os.path.curdir + r'\!PARSE_cinemas\*\*\Cinema.xml')
    xml_file = glob.glob(os.path.curdir + r'\Cinema.xml')
    while True:
        print("""
        1. Create stat-data for all xmls in <!PARSE_cinemas>
        2. Create stat-data & activation for 'Cinema.xml' in current dir
              """)
        choice = input('your choice: ')
        if choice == '1':
            if xml_folder:
                create_stat(get_xmls(xml_folder))
            else:
                logger.error('there are not xmls in <!PARSE_cinemas>')
            break
        elif choice == '2':
            if xml_file:
                create_stat(get_xmls(xml_file))
                create_active(get_xmls(xml_file))
            else:
                logger.error('there is not Cinema.xml in current dir')
            break
        else:
            logger.warning('incorrect input, try again')
    input('press <Enter> to exit...')
    logger.debug('-- end of log --')
    logger.debug('--/--')

if __name__ == '__main__':
    main()

