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
        logger.error('systeminfo.xmlb.xml was not found in ReportDir')
        return
    except IOError:
        logger.error('systeminfo.xmlb.xml was not copied in work dir')
        return
    logger.info('systeminfo.xmlb.xml was copied in work dir')
    return True

def get_marker(reporter_file):
    try:
        with open(reporter_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        logger.error('reporter.log was not found in ReportDir')
        return
    for line in lines:
        if 'Dongle marker' in line:
            marker = line.strip()[-19:]
            return marker

def get_seconds_from_marker(marker):
    split1 = marker.split(' ')
    split2 = split1[0].split('/')
    split3 = split1[1].split(':')
    struct_time = (
        int(split2[0]),
        int(split2[1]),
        int(split2[2]),
        int(split3[0]),
        int(split3[1]),
        int(split3[2]),
        0, 0, 0
    )
    tm = time.mktime(struct_time)
    return int(tm) + 62135694000

def set_tag_to_cinemasettings(tag, atr, value):
    tree = ET.parse('CinemaSettings.xml')
    tr = tree.find(tag)
    tr.set(atr, str(hex(value))[2:])
    tree.write('CinemaSettings.xml')
    logger.info(f'Acvation date {value} was set to CinemaSettings.xml ')

def prepare_regdata():
    cmd = r'Tools\ips_creator\prepareRegData.bat'
    code = subprocess.run(cmd, shell=False)
    if code.returncode == 0:
        logger.info('prepare regdata - ok')
    else:
        logger.error('prepare regdata - fail')

@endless_cycle
@check_input_date
def input_date_to_seconds(date):
    struct_time = (int('20' + date[4:]), int(date[2:4]), int(date[:2]), 0, 0, 0, 0, 0, 0)
    tm = time.mktime(struct_time)
    return int(tm) + 62135694000


def get_data_from_xml():
    activation = input_date_to_seconds(
        inp_date=input('input activation date: '),
        def_date=66206592000,
        key='activation'
    )
    validity = input_date_to_seconds(
        inp_date=input('input validity date: '),
        def_date=time.time() + 3600 + 62135694000,
        key='validity'
    )
    set_tag_to_cinemasettings('TR', 'D', activation)
    prepare_regdata()
    tree = ET.parse('Cinema.xml')
    root = tree.getroot()
    uid = root.attrib['UniqueId']
    try:
        with open(r'Tools\ips_creator\regdata.b64', 'r') as data:
            regdata = data.read()
    except FileNotFoundError:
        logger.error('regdata.b64 not found')
        return
    logger.info('All data have been taken')
    return int(validity), uid, regdata

def create_payload(validity, uid, regdata):
    root = ET.Element('IPSPayload')
    root.set('Validity', str(validity))
    root.set('UID', uid)
    root.set('Data', regdata)
    tree = ET.ElementTree(root)
    with open(r'Tools\ips_creator\Payload.xml', 'wb') as payload:
        tree.write(payload)
    logger.info('Payload.xml was prepared')

def prepare_payload(uid):
    cmd = r'Tools\ips_creator\preparePayload.bat'
    code = subprocess.run(cmd, shell=False)
    if code.returncode == 0:
        logger.info(f'IPS.exe for <{uid}> was created')
    else:
        logger.error('Creating IPS.exe failed')
        return


def main_ips_creator():
    subprocess.run(r'Tools\ips_creator\preautorun.bat', shell=False)

    while True:
        print("""
        <-- 
            1. Create IPS from CinemaSettings in work dir
            2. Create IPS from unpacked report (update "marker")
            3. Step back
              """)

        choice = input('your choice: ')

        if choice == '1':
            pass

        elif choice == '2':
            registry_file = r'ReportDir\systeminfo.xmlb.xml'
            reporter_file = r'ReportDir\reporter.log'

            if copy_registry_file(registry_file):
                marker = get_marker(reporter_file)
                print(marker)
            else:
                continue
            if marker:
                marker_seconds = get_seconds_from_marker(marker)
                set_tag_to_cinemasettings('D', 'M', marker_seconds)
            else:
                logger.warning('There is no marker in reporter.log')
                continue

        elif choice == '3':
            logger.debug('Back to the main menu')
            return

        c_file = r'Cinema.xml'
        cs_file = r'CinemaSettings.xml'
        if os.path.exists(c_file) and os.path.exists(cs_file):
            validity, uid, regdata = get_data_from_xml()
            create_payload(validity, uid, regdata)
            prepare_payload(uid)
        else:
            logger.error('There is no Cinema.xml or CinemaCinema.xml in work dir')
            return
