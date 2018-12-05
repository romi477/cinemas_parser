import subprocess
import os
import json
import re
import shutil
import glob
import logging
from pprint import pprint
from utils import check_dict_key
# from msvcrt import getch


logger = logging.getLogger('sccscript.unpackreport')

@check_dict_key
def parse_string(phrase, line):
    return ' '.join((line.split(']')[-1].split())) if phrase in line else None


def find_info_in_reporter():
    try:
        with open(r'ReportDir\reporter.log', 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
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
        uid = re.search(r'\w\w\w\w\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w\w\w\w\w\w\w\w\w', line)
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



def db_way(json_obj):
    iter_paths = glob.iglob(json_obj['path'], recursive=True)
    return [path for path in iter_paths if 'old' not in path]

def find_uid_in_db(paths_list, uid):
    logger.info('finding UID in database, please wait...')
    uid_list_from_db = []
    for path in paths_list:
        with open(path, 'r') as file:
            read_obj = file.read()
        uid_tmp = re.search(uid, read_obj)
        if uid_tmp:
            uid_list_from_db.append(path)
    return uid_list_from_db

def go_path(path):
    abs_path = os.path.abspath(path)
    abs_path = abs_path.split(r'\Cinema.xml')[0]
    proc = r'explorer.exe /n, {}'.format(abs_path)
    subprocess.run(proc, shell=True)

def copy_cinema_to_workdir(path):
    abs_path = os.path.abspath(path).split(r'Cinema.xml')[0]
    try:
        shutil.copy2(os.path.join(abs_path, r'Cinema.xml'), 'Cinema.xml')
    except IOError:
        logger.error('Cinema.xml has not been copied to the work dir')
        return
    try:
        shutil.copy2(os.path.join(abs_path, r'CinemaSettings.xml'), 'CinemaSettings.xml')
    except IOError:
        logger.error('CinemaSettings.xml has not been copied to the work dir')
        return
    logger.info('Cinema.xml has been copied to the work dir')
    logger.info('CinemaSettings.xml has been copied to the work dir')

def print_func(def_value, value):
    print(value) if value else print(def_value)

def main_find_uid():
    if os.path.exists('ReportDir'):
        logger.info('<ReportDir> is deleting, please wait...')
        shutil.rmtree('ReportDir', ignore_errors=True)

    subprocess.run(r'Tools\unpack_report\start_unpack.bat', shell=False)
    print()
    try:
        with open('config.json', 'r', encoding='utf8') as file:
            json_obj = json.load(file)
    except FileNotFoundError:
        logger.error('config.json has not been found in work dir!!!')
        input('press <Enter> to return...')
        print('----------------------------')
        return
    paths_list = db_way(json_obj)
    info_from_reporter = find_info_in_reporter()

    if info_from_reporter:
        if info_from_reporter['registry_uid'] and info_from_reporter['dongle_uid']:
            if info_from_reporter['registry_uid'] == info_from_reporter['dongle_uid']:
                list_paths_in_db = find_uid_in_db(paths_list, info_from_reporter['dongle_uid'])
            else:
                logger.warning('dongle UID is not equal registry UID !!!')
                input('press <Enter> to return...')
                print('----------------------------')
                return
        else:
            if info_from_reporter['dongle_uid']:
                list_paths_in_db = find_uid_in_db(paths_list, info_from_reporter['dongle_uid'])
            elif info_from_reporter['registry_uid']:
                list_paths_in_db = find_uid_in_db(paths_list, info_from_reporter['registry_uid'])
            else:
                logger.warning('none UID has not been found in ReportDir/reporter.log')
                input('press <Enter> to return...')
                print('----------------------------')
                return
    else:
        logger.error(r'ReportDir\reporter.log not found')
        input('press <Enter> to return...')
        print('----------------------------')
        return

    if list_paths_in_db:
        print('----------------------------')
        print('  REPORTER INFO:')
        print_func('Trial date:', info_from_reporter['trial_date'])
        print_func('Registry marker:', info_from_reporter['registry_marker'])
        print_func('Dongle marker:', info_from_reporter['dongle_marker'])
        print(f'Registry UID: {info_from_reporter["registry_uid"]}')
        print_func('SCCFM version:', info_from_reporter['sccfm_version'])
        print_func('RTC UNC clock time:', info_from_reporter['rtc_unc'])
        print_func('HOST UNC clock time:', info_from_reporter['host_unc'])
        print(f'Dongle UID: {info_from_reporter["dongle_uid"]}')
        print('  FOUND PATHS:')
        pprint(list_paths_in_db)
        print('----------------------------')
        input('press <Enter> to return...')

        if len(list_paths_in_db) == 1:
            copy_cinema_to_workdir(list_paths_in_db[0])
            print('----------------------------')
        else:
            logger.warning('more then one UID exist in database')
            logger.warning('xmls have not been copied to the work dir')
            print('----------------------------')

        for path in list_paths_in_db:
            go_path(path)
            print('----------------------------')


