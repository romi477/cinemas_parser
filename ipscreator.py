import subprocess
import xml.etree.ElementTree as ET
import sys
import os
import json
from datetime import datetime
import time
import logging


date_today = datetime.today()
if not os.path.exists('logs'):
    os.mkdir('logs')
pth = f'logs\{date_today.strftime("%m-%Y")}'
if not os.path.exists(pth):
    os.mkdir(pth)

logger = logging.getLogger('ipscreator')
logger.setLevel(logging.DEBUG)

ch1 = logging.StreamHandler()
ch1.setLevel(logging.INFO)
ch2 = logging.FileHandler(filename=pth + f'\{date_today.strftime("%d-%m-%Y")}.log', delay=False)
ch2.setLevel(logging.DEBUG)

formatter1 = logging.Formatter('[%(levelname)s] <%(funcName)s> %(message)s')
formatter2 = logging.Formatter('[%(asctime)s %(levelname)s] <%(funcName)s> %(message)s', '%d/%m/%Y %H:%M:%S')

ch1.setFormatter(formatter1)
ch2.setFormatter(formatter2)
logger.addHandler(ch1)
logger.addHandler(ch2)


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
    # logger.debug('--- <IPS_create> log started ---')
    filesForDelete = [
        'IPS.exe',
        r'Tools\ips_creator\payload.bin',
        r'Tools\ips_creator\Payload.xml',
        r'Tools\ips_creator\regdata.b64'
    ]
    for file in filesForDelete:
        try:
            os.remove(file)
            logger.info(f'{file} was removed')
        except FileNotFoundError:
            logger.warning(f"{file} wasn't found")
            pass
    validity, uid, data = get_all_data()
    create_payload(validity, uid, data)
    prepare_payload(uid)
    # input('press <Enter> to exit...')
    # logger.debug('--- <IPS_create> log stopped ---\n')

