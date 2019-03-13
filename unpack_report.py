import subprocess
import os
import json
from re import search
import shutil
import glob
import logging
from pprint import pprint
import xml.etree.ElementTree as ET
from utils import copy_file

logger = logging.getLogger('sccscript.unpackreport')

def parse_string(phrase, line, dct, key):
    if phrase in line:
        dct[key] = ' '.join((line.split(']')[-1].split()))
    return dct

def find_info_in_reporter():
    try:
        with open(r'ReportDir\reporter.log', 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        logger.error(r'ReportDir\reporter.log  has not been found')
        return
    reporter_dict = dict.fromkeys(
        [
            'registry_uid',
            'dongle_uid',
            'sccfm_version',
            'trial_date',
            'registry_marker',
            'dongle_marker',
            'rtc_unc',
            'host_unc'
        ]
    )
    for line in lines:
        uid = search(r'\w\w\w\w\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w\w\w\w\w\w\w\w\w', line)
        if uid:
            if 'Instance UID' in line:
                reporter_dict['registry_uid'] = uid.group(0)
            elif 'SCC UID from dongle' in line:
                reporter_dict['dongle_uid'] = uid.group(0)

        parse_string('Dongle SCCFW version', line, dct=reporter_dict, key='sccfm_version')
        parse_string('Trial end date', line, dct=reporter_dict, key='trial_date')
        parse_string('Marker Date', line, dct=reporter_dict, key='registry_marker')
        parse_string('Dongle marker', line, dct=reporter_dict, key='dongle_marker')
        parse_string('RTC UNC clock time', line, dct=reporter_dict, key='rtc_unc')
        parse_string('Host UNC clock time', line, dct=reporter_dict, key='host_unc')
    return reporter_dict

def db_way(config):
    iter_list = config['db_path'] + '\\*\\*\\**\\Cinema.xml'
    iter_paths = glob.iglob(iter_list, recursive=True)
    return [path for path in iter_paths if 'old' not in path]

def find_uid_in_db(paths_list, uid):
    logger.info('Finding UID in database, please wait...')
    uid_list_from_db = []
    for path in paths_list:
        with open(path, 'r') as file:
            read_obj = file.read()
        uid_tmp = search(uid, read_obj)
        if uid_tmp:
            uid_list_from_db.append(path)
    return uid_list_from_db

def go_path(path):
    abs_path = os.path.abspath(path)
    abs_path = abs_path.split(r'\Cinema.xml')[0]
    proc = r'explorer.exe /n, {}'.format(abs_path)
    subprocess.run(proc, shell=True)

def print_func(def_value, value):
    if value:
        split_list = value.split(': ')
        try:
            result_value = '{:22} {}'.format(split_list[0].strip() + ':', split_list[1].strip())
        except IndexError:
            result_value = '{:22} {}'.format(split_list[0].strip() + ':', None)
        print(result_value)
    else:
        print(def_value)

def print_dict(dct):
    print('---------------------------------------')
    print(f'{"":<16}FOUND PATHS:')
    for k, v in dct.items():
        print(f'{k}:')
        pprint(v)
    print('---------------------------------------')

def movie_parser(movie_pth):
    root = ET.parse(movie_pth).getroot()
    expired = root.find('Expired')
    try:
        license = expired.get('Value')
        return license
    except AttributeError:
        pass


def walk_pth(pth):
    content_list = []
    iter_movies = glob.glob(pth + r'\\*\\*.xml')
    for idx, movie_pth in enumerate(iter_movies, 1):
        movie_license = movie_parser(movie_pth)
        mps = movie_pth.split(os.path.sep)
        if movie_license:
            print(f'{"/".join(mps[-3:-1]):<26} {idx}. {mps[-1].split(".")[-2]}: {movie_license}')
            content_list.append(f'{"/".join(mps[-3:-1]):<26} {idx}. {mps[-1].split(".")[-2]}: {movie_license}')
        else:
            print(f'{"/".join(mps[-3:-1]):<26} {idx}. {mps[-1].split(".")[-2]}')
            content_list.append(f'{"/".join(mps[-3:-1]):<26} {idx}. {mps[-1].split(".")[-2]}')
    content_list.append('')
    return content_list

def main_find_uid_inner():
    if not os.path.exists('ReportDir'):
        logger.error('<ReportDir> does not exist!')
        logger.info('Make sure that SCC2Report.pak was unpacked at <ReportDir> directory!')
        return
    try:
        with open('config.json', 'r', encoding='utf8') as file:
            config = json.load(file)
    except FileNotFoundError:
        logger.error('config.json has not been found in work dir!!!')
        input('Press <Enter> to return...')
        return
    paths_list = db_way(config)
    reporter_dict = find_info_in_reporter()

    if reporter_dict:
        print('---------------------------------------')
        print(f'{"":<16}REPORTER INFO:')
        print_func('Trial end date:        None', reporter_dict['trial_date'])
        print_func('Registry marker:       None', reporter_dict['registry_marker'])
        print_func('Dongle marker:         None', reporter_dict['dongle_marker'])
        print(f'Registry UID:          {reporter_dict["registry_uid"]}')
        print_func('SCCFM version:         None', reporter_dict['sccfm_version'])
        print_func('RTC UNC clock time:    None', reporter_dict['rtc_unc'])
        print_func('HOST UNC clock time:   None', reporter_dict['host_unc'])
        print(f'Dongle UID:            {reporter_dict["dongle_uid"]}')
        print('---------------------------------------')

        while True:
            print("""   
            <--     
                1. Find UID in database
                2. Analyze content
                3. Main menu
                      """)
            choice = input('your choice: ')
            if choice == '1':
                uid_list_from_db = {}
                if reporter_dict['registry_uid'] and reporter_dict['dongle_uid']:
                    if reporter_dict['registry_uid'] == reporter_dict['dongle_uid']:
                        logger.info('Dongle UID is equal Registry UID')
                        uid_list_from_db['Dongle_UID'] = find_uid_in_db(paths_list, reporter_dict['dongle_uid'])
                    else:
                        logger.warning('Dongle UID is not equal Registry UID !!!')
                        uid_list_from_db['Dongle_UID'] = find_uid_in_db(paths_list, reporter_dict['dongle_uid'])
                        uid_list_from_db['Registry_UID'] = find_uid_in_db(paths_list, reporter_dict['registry_uid'])
                        print_dict(uid_list_from_db)
                        print('---------------------------------------')
                        continue
                else:
                    if reporter_dict['dongle_uid']:
                        logger.warning('Only Dongle UID has been parsed from reporter.log')
                        uid = find_uid_in_db(paths_list, reporter_dict['dongle_uid'])
                        if uid:
                            uid_list_from_db['Dongle_UID'] = uid
                    elif reporter_dict['registry_uid']:
                        logger.warning('Only Registry UID has been parsed from reporter.log')
                        uid = find_uid_in_db(paths_list, reporter_dict['registry_uid'])
                        if uid:
                            uid_list_from_db['Registry_UID'] = uid
                    else:
                        logger.warning('None UID has been found in reporter.log')
                        print('---------------------------------------')
                        continue

                if uid_list_from_db:
                    print_dict(uid_list_from_db)
                    try:
                        path_xml = uid_list_from_db['Dongle_UID']
                    except KeyError:
                        path_xml = uid_list_from_db['Registry_UID']
                    if len(path_xml) == 1:
                        choice = input('Press <Enter> to copy files to the work dir')
                        if choice == '':
                            abs_path_xml = os.path.abspath(path_xml[0]).split(r'Cinema.xml')[0]
                            copy_file(os.path.join(abs_path_xml, r'Cinema.xml'), 'Cinema.xml')
                            copy_file(os.path.join(abs_path_xml, r'CinemaSettings.xml'), 'CinemaSettings.xml')
                        else:
                            logger.info('Copying files has been skipped')

                        choice = input('Press <Enter> to go to the path')
                        if choice == '':
                            for path in uid_list_from_db:
                                go_path(path)
                    else:
                        logger.warning('More than one UID exists in database')
                        print('---------------------------------------')
                        continue
                else:
                    logger.warning('None UID has been found in Database')
                    print('---------------------------------------')
                    continue
                print('---------------------------------------')

            elif choice == '2':
                print('---------------------------------------')
                print(f'{"":<16}CONTENT:')
                full_content_list = []
                for pth in config['content_dirs']:
                    if os.path.exists(pth) and os.listdir(pth):
                        full_content_list.extend(walk_pth(pth))
                if full_content_list:
                    with open('content.txt', 'w') as txt_file:
                        for line in full_content_list:
                            txt_file.write(line + '\n')
                else:
                    logger.warning('Content has not been found')
                print('---------------------------------------')
            elif choice == '3':
                break
    else:
        logger.warning('<Reporter info> has not been parsed')


def main_find_uid():
    if os.path.exists('ReportDir'):
        logger.info('<ReportDir> is being deleted, please wait...')
        try:
            shutil.rmtree('ReportDir')
        except Exception as e:
            logger.error(e)
            logger.error('Try to rename the directory <Reportdir>')
            input('Press <Enter> to return...')
            return
    subprocess.run(r'Tools\unpack_report\start_unpack.bat')
    print()
    main_find_uid_inner()



