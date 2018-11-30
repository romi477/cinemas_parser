import subprocess
import xml.etree.ElementTree as ET
import sys
import json
import time
import logging


logger = logging.getLogger('sccscript.ipscreator')

def prepare_regdata():
    cmd = r'Tools\ips_creator\prepareRegData.bat'
    code = subprocess.run(cmd, shell=False)
    if code.returncode == 0:
        logger.info('ok')
    else:
        logger.error('fail')
        sys.exit(1)

def edit_cinemasettings(activation):
    tree = ET.parse('CinemaSettings.xml')
    tr = tree.find('TR')
    tr.set('D', str(hex(activation))[2:])
    tree.write('CinemaSettings.xml')
    logger.info('ok')

def get_seconds(date):
    d = date.split('/')
    struct_time = (int(d[2]), int(d[1]), int(d[0]), 0, 0, 0, 0, 0, 0)
    tm = time.mktime(struct_time)
    logger.info('ok')
    return int(tm) + 62135694000

def get_all_data():
    with open(r'config.json') as file:
        config = json.load(file)
    activation = get_seconds(config['activation'])
    validity = get_seconds(config['validity'])
    edit_cinemasettings(activation)
    prepare_regdata()
    tree = ET.parse('Cinema.xml')
    root = tree.getroot()
    uid = root.attrib['UniqueId']
    with open(r'Tools\ips_creator\regdata.b64') as regdata:
        data = regdata.read()
    logger.info('ok')
    return validity, uid, data

def create_payload(validity, uid, data):
    root = ET.Element('IPSPayload')
    root.set('Validity', str(validity))
    root.set('UID', uid)
    root.set('Data', data)
    tree = ET.ElementTree(root)
    with open(r'Tools\ips_creator\Payload.xml', 'wb') as payload:
        tree.write(payload)
    logger.info('ok')

def prepare_payload(uid):
    cmd = r'Tools\ips_creator\preparePayload.bat'
    code = subprocess.run(cmd, shell=False)
    if code.returncode == 0:
        logger.info(f'IPS.exe for <{uid}> was created')
    else:
        logger.error('fail')
        sys.exit(1)


def main_ips_creator():
    subprocess.run(r'Tools\ips_creator\preautorun.bat', shell=False)

    while True:
        print("""
        <-- 
            1. Create IPS from CinemaSettings.xml in work dir
            2. Create IPS from unpacked report (update "marker")
            3. Step back
              """)

        validity, uid, data = get_all_data()
        create_payload(validity, uid, data)
        prepare_payload(uid)
