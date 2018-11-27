import subprocess
import xml.etree.ElementTree as ET
import os
import sys
import glob
from datetime import datetime
from re import fullmatch
import logging
from findUID import main_find_uid
from ipscreator import main_ips_creator


activCmd = r'Tools\activ_stat\XmlSigner.exe -sign -key Tools\activ_stat\ActivationKey.RSAPrivate -file Activation.xml.xml'
statCmd = r'Tools\activ_stat\XmlSigner.exe -sign -key Tools\activ_stat\OwnerIDSignKey.RSAPrivate -file Statistics.key.xml'
compressActiv = r'Tools\activ_stat\Compressor.exe compress Activation.xml.xml Activation.xml -mtf'
compressStat = r'Tools\activ_stat\Compressor.exe compress Statistics.key.xml Statistics.key -mtf'

date = datetime.today()
if not os.path.exists('logs'):
    os.mkdir('logs')
pth = f'logs\{date.strftime("%m-%Y")}'
if not os.path.exists(pth):
    os.mkdir(pth)

logger = logging.getLogger('createActivStat')
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

def xml_data(file):
    tree = ET.ElementTree(file=file)
    root = tree.getroot()
    title = root.attrib['title']
    uid = root.attrib['UniqueId']
    owner = tree.find('Owner').attrib['Value']
    return {'title': title, 'uid': uid, 'owner': owner}

def evaluate_path(pth):
    try:
        dir_name = pth.split(os.path.sep)[1]
    except IndexError:
        return xml_data(pth)
    if dir_name.startswith('-'):
        logger.info(f'{pth} was skipped')
        return None
    else:
        return xml_data(pth)

def create_single_stat(dct):
    cinema = ET.Element('Cinema')
    cinema.set('Name', f'{dct["title"]}-{dct["owner"]}')
    cinema.set('UID', f'{dct["uid"]}')
    return cinema

def create_stat(lst):
    root = ET.Element('StatisticsExportKey')
    for d in lst:
        root.append(create_single_stat(d))
        logger.info(f'Statistics for {d["title"]} <{d["uid"]}> was created')
    tree = ET.ElementTree(root)
    with open('Statistics.key.xml', 'wb') as f:
        tree.write(f)
    logger.info(f'Statistics.key.xml was written')

def create_activ(dct, activation_date):
    format_date = f'20{activation_date[4:]}/{activation_date[2:4]}/{activation_date[:2]}'
    root = ET.Element('Activation')
    root.set('UID', f'{dct["uid"]}')
    root.set('Expiration', format_date)
    tree = ET.ElementTree(root)
    logger.info(f'Activation for <{dct["uid"]}> in <{activation_date}> was created')
    with open('Activation.xml.xml', 'wb') as f:
        tree.write(f)
    logger.info(f'Activation.xml.xml was written')

def sign_compress(cmd, compress):
    sign = subprocess.run(cmd, shell=False)
    if sign.returncode == 0:
        logger.info(f'{cmd} - OK')
        code = subprocess.run(compress, shell=False)
        if code.returncode == 0:
            logger.info(f'{compress} - OK')
        else:
            logger.warning(f'{compress} - FAIL')
    else:
        logger.warning(f'{cmd} - FAIL')


def main():
    logger.debug('--- Log started ---')
    files_for_delete = ['Activation.xml.xml', 'Activation.xml', 'Statistics.key.xml', 'Statistics.key']
    for file in files_for_delete:
        try:
            os.remove(file)
            logger.debug(f'{file} was removed')
        except FileNotFoundError:
            logger.debug(f"{file} was't found" )
            pass

    while True:
        print("""
        1. Create statistics and activation
        2. Find UID from SCC2report.pack in database
        3. Create IPS.exe
        4. Quit
              """)
        choice = input('your choice: ')

        if choice == '1':
            while True:
                print("""
            1. Create statistics for all xmls in <!Cinemas>
            2. Create statistics & activation for Cinema.xml in current dir
            3. Step back
                      """)
                choice2 = input('your choice: ')
                activCmd = r'Tools\activ_stat\XmlSigner.exe -sign -key Tools\activ_stat\ActivationKey.RSAPrivate -file Activation.xml.xml'
                statCmd = r'Tools\activ_stat\XmlSigner.exe -sign -key Tools\activ_stat\OwnerIDSignKey.RSAPrivate -file Statistics.key.xml'
                compressActiv = r'Tools\activ_stat\Compressor.exe compress Activation.xml.xml Activation.xml -mtf'
                compressStat = r'Tools\activ_stat\Compressor.exe compress Statistics.key.xml Statistics.key -mtf'

                if choice2 == '1':
                    paths_list = glob.glob(r'!Cinemas\*\*\Cinema.xml')
                    if paths_list:
                        xmls_data_list = [evaluate_path(i) for i in paths_list if evaluate_path(i)]
                        if xmls_data_list:
                            create_stat(xmls_data_list)
                            sign_compress(statCmd, compressStat)
                            break
                        else:
                            logger.error('All xmls were skipped')
                            break
                    logger.error('There are no xmls in <!Cinemas>')
                    break
                elif choice2 == '2':
                    xml_file = 'Cinema.xml'
                    if not os.path.exists(xml_file):
                        logger.error('There is no Cinema.xml in current dir')
                        break
                    while True:
                        activation_date = input('enter activation date: ')
                        if not activation_date:
                            activation_date = '010199'
                        if fullmatch(r'\d\d\d\d\d\d', activation_date):
                            create_stat([evaluate_path(xml_file)])
                            sign_compress(statCmd, compressStat)
                            create_activ(evaluate_path(xml_file), activation_date)
                            sign_compress(activCmd, compressActiv)
                            break
                        else:
                            logger.warning('Enter activation date as <%d%m%y>, for example: 010199,\n'
                                           '          or press <Enter> to set default date = 010199')
                            print('-----------------------------------------------------------------\n')
                    break
                elif choice2 == '3':
                    break
                else:
                    logger.error('incorrect input, try again')
                break

        elif choice == '2':
            main_find_uid()
        elif choice == '3':
            main_ips_creator()
        elif choice == '4':
            logger.info('Quit')
            logger.debug('--- Log stopped ---\n')
            sys.exit(0)
        else:
            logger.error('incorrect input, try again')
            print('************************************')



if __name__ == '__main__':
    main()

