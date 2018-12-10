import subprocess
import xml.etree.ElementTree as ET
import os
import time
import logging
from re import search
from utils import check_input_date, endless_cycle, copy_file


logger = logging.getLogger('sccscript.ipscreator')

def get_marker(reporter_file):
    try:
        with open(reporter_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error(r'ReportDir\reporter.log has not been found')
        return
    for line in lines:
        if 'Dongle marker' in line:
            marker = search(r' \d\d\d\d/\d\d/\d\d \d\d:\d\d:\d\d', line)
            if marker:
                return marker.group(0)[1:] if marker.group(0)[1:] != '1970/01/01 00:00:00' else '1970/01/01 03:00:00'
            else:
                logger.error(r'Dongle marker in ReportDir\reporter.log has not been found')
                return
    logger.error(r'Dongle marker in ReportDir\reporter.log has not been found')
    return

def get_seconds_from_marker(marker):
    arg1 = marker.split()[0].split('/')
    arg2 = marker.split()[1].split(':')
    struct_time = (int(arg1[0]), int(arg1[1]), int(arg1[2]), int(arg2[0]), int(arg2[1]), int(arg2[2]), 0, 0, 0)
    tm = time.mktime(struct_time)
    logger.info('Seconds from marker have been taken')
    return int(tm) + 62135694000

def set_tag_to_cinemasettings(tag, atr, value):
    try:
        tree = ET.parse('CinemaSettings.xml')
    except ET.ParseError:
        logger.error('CinemaSettings.xml have a parseerror-mistake')
    else:
        tr = tree.find(tag)
        tr.set(atr, str(hex(value))[2:])
        tree.write('CinemaSettings.xml')
        logger.info(f'<{tag}> {atr} = {value} </{tag}> has been set to CinemaSettings.xml ')
        return True

@endless_cycle
@check_input_date
def input_date_to_seconds(inp_date, def_date, key):
    struct_time = (int('20' + inp_date[4:]), int(inp_date[2:4]), int(inp_date[:2]), 0, 0, 0, 0, 0, 0)
    tm = time.mktime(struct_time)
    return int(tm) + 62135694000

def get_data_from_xmls(cmd):
    logger.debug('Getting data from xmls has been started')
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
    logger.info('All data from xmls has been taken')
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
            1. Create IPS from Cinema-CinemaSettings in work dir
            2. Create IPS from unpacked report & update "marker"
            3. Main menu
              """)
        choice = input('your choice: ')
        if choice == '1':
            subprocess.run(r'Tools\ips_creator\preautorun.bat', shell=False)
            break
        elif choice == '2':
            subprocess.run(r'Tools\ips_creator\preautorun.bat', shell=False)
            print()
            registry_file = r'ReportDir\systeminfo.xmlb.xml'
            reporter_file = r'ReportDir\reporter.log'
            abs_path = os.path.abspath(registry_file)
            if copy_file(abs_path, 'CinemaSettings.xml'):
                marker = get_marker(reporter_file)
            else:
                input('Press <Enter> to return...')
                return
            if marker:
                marker_seconds = get_seconds_from_marker(marker)
                set_marker = set_tag_to_cinemasettings('D', 'M', marker_seconds)
                if not set_marker:
                    input('Press <Enter> to return...')
                    return
                break
            else:
                input('Press <Enter> to return...')
                return
        elif choice == '3':
            logger.debug('Back to main menu')
            return
        else:
            logger.error('Incorrect input, try again')
            print('----------------------------')

    if os.path.exists('Cinema.xml') and os.path.exists('CinemaSettings.xml'):
        regdata_cmd = r'Tools\ips_creator\prepareRegData.bat'
        print()
        data_from_xmls = get_data_from_xmls(regdata_cmd)
        if data_from_xmls:
            create_payload(**data_from_xmls)
            payload_cmd = r'Tools\ips_creator\preparePayload.bat'
            subprocess.run(payload_cmd, shell=False)
            logger.info(f'IPS.exe for <{data_from_xmls["uid"]}> was created')
        else:
            logger.error('Data from xmls has not been taken')
            input('Press <Enter> to return...')
    else:
        logger.error('There is no Cinema.xml or CinemaCinema.xml in work dir')
        input('Press <Enter> to return...')

