import subprocess
import xml.etree.ElementTree as ET
import shutil
import os
import time
import logging
from utils import check_input_date, endless_cycle


logger = logging.getLogger('sccscript.ipscreator')

def copy_registry_file(registry_file):
    try:
        shutil.copy2(registry_file, 'CinemaSettings.xml')
    except FileNotFoundError:
        logger.error(r'ReportDir\systeminfo.xmlb.xml has not been found')
        return
    except IOError:
        logger.error(r'ReportDir\systeminfo.xmlb.xml has not been copied')
        return
    logger.info(r'ReportDir\systeminfo.xmlb.xml has been copied')
    return True

def get_marker(reporter_file):
    try:
        with open(reporter_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error(r'ReportDir\reporter.log was not found')
        return
    for line in lines:
        if 'Dongle marker' in line:
            marker = line.strip()[-19:]
            return marker if marker != '1970/01/01 00:00:00' else '1970/01/01 03:00:00'

def get_seconds_from_marker(marker):
    arg1 = marker.split()[0].split('/')
    arg2 = marker.split()[1].split(':')
    struct_time = (int(arg1[0]), int(arg1[1]), int(arg1[2]), int(arg2[0]), int(arg2[1]), int(arg2[2]), 0, 0, 0)
    tm = time.mktime(struct_time)
    logger.info('seconds from marker have been taken')
    return int(tm) + 62135694000

def set_tag_to_cinemasettings(tag, atr, value):
    try:
        tree = ET.parse('CinemaSettings.xml')
    except ET.ParseError:
        logger.error('CinemaSettings.xml have a parseerror-mistake')
        return
    tr = tree.find(tag)
    tr.set(atr, str(hex(value))[2:])
    tree.write('CinemaSettings.xml')
    logger.info(f'<{tag}> {atr} = {value} </{tag}> has been set to CinemaSettings.xml ')
    return True

@endless_cycle
@check_input_date
def input_date_to_seconds(inp_date):
    struct_time = (int('20' + inp_date[4:]), int(inp_date[2:4]), int(inp_date[:2]), 0, 0, 0, 0, 0, 0)
    tm = time.mktime(struct_time)
    return int(tm) + 62135694000


def get_data_from_xmls(cmd):
    logger.debug('getting data from xmls has been started')
    activation = input_date_to_seconds(
        inp_date=input('activation date: '),
        def_date=66206592000,
        key='activation'
    )
    validity = input_date_to_seconds(
        inp_date=input('validity date: '),
        def_date=time.time() + 86400 + 62135694000,
        key='validity'
    )
    if not set_tag_to_cinemasettings('TR', 'D', activation):
        return False
    subprocess.run(cmd, shell=False)
    tree = ET.parse('Cinema.xml')
    root = tree.getroot()
    uid = root.attrib['UniqueId']
    try:
        with open(r'Tools\ips_creator\regdata.b64', 'r') as data:
            regdata = data.read()
    except FileNotFoundError:
        logger.error(r'Tools\ips_creator\regdata.b64 not found')
        return
    logger.info('all data from xmls has been taken')
    return {'validity': int(validity), 'uid': uid, 'regdata': regdata}

def create_payload(validity, uid, regdata):
    root = ET.Element('IPSPayload')
    root.set('Validity', str(validity))
    root.set('UID', uid)
    root.set('Data', regdata)
    tree = ET.ElementTree(root)
    with open(r'Tools\ips_creator\Payload.xml', 'wb') as payload:
        tree.write(payload)
    logger.info(r'Tools\ips_creator\Payload.xml was prepared')


def main_ips_creator():
    while True:
        print("""
        <-- 
            1. Create IPS from CinemaSettings in work dir
            2. Create IPS from unpacked report (update "marker")
            3. Main menu
              """)
        choice = input('your choice: ')
        if choice == '1':
            subprocess.run(r'Tools\ips_creator\preautorun.bat', shell=False)
            print()
        elif choice == '2':
            subprocess.run(r'Tools\ips_creator\preautorun.bat', shell=False)
            print()
            registry_file = r'ReportDir\systeminfo.xmlb.xml'
            reporter_file = r'ReportDir\reporter.log'
            if copy_registry_file(registry_file):
                marker = get_marker(reporter_file)
            else:
                input('press <Enter> to return...')
                print('----------------------------')
                break
            if marker:
                marker_seconds = get_seconds_from_marker(marker)
                set_marker = set_tag_to_cinemasettings('D', 'M', marker_seconds)
                if not set_marker:
                    input('press <Enter> to return...')
                    print('----------------------------')
                    break
            else:
                logger.warning(r'there is no marker in ReportDir\reporter.log')
                input('press <Enter> to return...')
                print('----------------------------')
                break
        elif choice == '3':
            logger.debug('back to main menu')
            break
        else:
            logger.error('incorrect input, try again')
            print('----------------------------')

        if os.path.exists('Cinema.xml') and os.path.exists('CinemaSettings.xml'):
            regdata_cmd = r'Tools\ips_creator\prepareRegData.bat'
            data_from_xmls = get_data_from_xmls(regdata_cmd)
            if data_from_xmls:
                create_payload(**data_from_xmls)
                payload_cmd = r'Tools\ips_creator\preparePayload.bat'
                subprocess.run(payload_cmd, shell=False)
                logger.info(f'IPS.exe for <{data_from_xmls["uid"]}> was created')
            else:
                logger.error('data from xmls has not been taken')
                input('press <Enter> to return...')
                print('----------------------------')
                break
        else:
            logger.error('there is no Cinema.xml or CinemaCinema.xml in work dir')
            input('press <Enter> to return...')
            print('----------------------------')
            break
