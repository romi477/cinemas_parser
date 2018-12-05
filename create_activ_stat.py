import subprocess
import xml.etree.ElementTree as ET
import os
import glob
import logging
from utils import check_input_date, endless_cycle, sign_compress


logger = logging.getLogger('sccscript.createactivstat')

def get_xml_data_dict(file):
    try:
        tree = ET.ElementTree(file=file)
    except ET.ParseError:
        logger.error('Cinema.xml have a parseerror-mistake')
        return
    root = tree.getroot()
    title = root.attrib['title']
    uid = root.attrib['UniqueId']
    try:
        owner = tree.find('Owner').attrib['Value']
    except AttributeError:
        owner = tree.find('OwnerPassword').attrib['Value']
    return {'title': title, 'uid': uid, 'owner': owner}

def evaluate_path(pth):
    try:
        dir_name = pth.split(os.path.sep)[1]
    except IndexError:
        return get_xml_data_dict(pth)
    if dir_name.startswith('-'):
        logger.info(f'{pth} has been skipped')
        return None
    else:
        return get_xml_data_dict(pth)

def create_single_stat(xml_dict):
    cinema = ET.Element('Cinema')
    cinema.set('Name', f'{xml_dict["title"]}-{xml_dict["owner"]}')
    cinema.set('UID', f'{xml_dict["uid"]}')
    return cinema

def create_stat(xml_dict_list):
    root = ET.Element('StatisticsExportKey')
    for xml_dict in xml_dict_list:
        root.append(create_single_stat(xml_dict))
        logger.info(f'Statistics for {xml_dict["title"]} <{xml_dict["uid"]}> has been created')
    tree = ET.ElementTree(root)
    with open('Statistics.key.xml', 'wb') as f:
        tree.write(f)
    logger.info(f'Statistics.key.xml has been written')

@endless_cycle
@check_input_date
def get_time(inp_date):
    return f'20{inp_date[4:]}/{inp_date[2:4]}/{inp_date[:2]}'

def create_activ(cinema_dict):
    format_date = get_time(
        inp_date=input('activation date: '),
        def_date='2099/01/01',
        key='activation'
    )
    root = ET.Element('Activation')
    root.set('UID', f'{cinema_dict["uid"]}')
    root.set('Expiration', format_date)
    tree = ET.ElementTree(root)
    logger.info(f'Activation.xml.xml for <{cinema_dict["uid"]}> in <{format_date}> has been created')
    with open('Activation.xml.xml', 'wb') as f:
        tree.write(f)
    logger.info(f'Activation.xml.xml has been written')


def main_create_activstat():

    activ_cmd = r'Tools\activ_stat\XmlSigner.exe -sign -key Tools\activ_stat\ActivationKey.RSAPrivate -file Activation.xml.xml'
    stat_cmd = r'Tools\activ_stat\XmlSigner.exe -sign -key Tools\activ_stat\OwnerIDSignKey.RSAPrivate -file Statistics.key.xml'
    compress_activ = r'Tools\activ_stat\Compressor.exe compress Activation.xml.xml Activation.xml -mtf'
    compress_stat = r'Tools\activ_stat\Compressor.exe compress Statistics.key.xml Statistics.key -mtf'

    while True:
        print("""
        <-- 
            1. Create statistics for all xmls in <!Cinemas>
            2. Create statistics & activation for Cinema.xml in work dir
            3. Main menu
              """)
        choice = input('your choice: ')
        if choice == '1':
            subprocess.run(r'Tools\activ_stat\preautorun.bat', shell=False)
            print()
            paths_list = glob.iglob(r'!Cinemas\*\*\Cinema.xml')
            if paths_list:
                xmls_data_list = [evaluate_path(i) for i in paths_list if evaluate_path(i)]
                if xmls_data_list:
                    create_stat(xmls_data_list)
                    sign_compress(stat_cmd, compress_stat)
                    print('----------------------------')
                    break
                else:
                    logger.warning('all xmls were skipped')
                    input('press <Enter> to return...')
                    print('----------------------------')
                    break
            else:
                logger.error('there are no xmls in <!Cinemas>')
                input('press <Enter> to return...')
                print('----------------------------')
                break

        elif choice == '2':
            subprocess.run(r'Tools\activ_stat\preautorun.bat', shell=False)
            print()
            xml_file = 'Cinema.xml'
            if os.path.exists(xml_file):
                xml_data_dict = get_xml_data_dict(xml_file)
                if xml_data_dict:
                    create_activ(xml_data_dict)
                    create_stat([xml_data_dict])
                    sign_compress(activ_cmd, compress_activ)
                    sign_compress(stat_cmd, compress_stat)
                    break
                else:
                    input('press <Enter> to return...')
                    print('----------------------------')
                    break
            else:
                logger.error('there is no Cinema.xml in work dir')
                input('press <Enter> to return...')
                print('----------------------------')
                break
        elif choice == '3':
            logger.debug('back to the main menu')
            print('----------------------------')
            break
        else:
            logger.error('incorrect input, try again')
            print('----------------------------')


