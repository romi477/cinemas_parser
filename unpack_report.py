import subprocess
import os
import json
from re import search
import shutil
import glob
import logging
from pprint import pprint
from utils import copy_file
# from msvcrt import getch


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

def db_way(json_obj):
    iter_paths = glob.iglob(json_obj['path'], recursive=True)
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

def main_find_uid():
    if os.path.exists('ReportDir'):
        logger.info('<ReportDir> is being deleted, please wait...')
        try:
            shutil.rmtree('ReportDir')
        except PermissionError:
            logger.error('<Reportdir> has not been deleted')
            input('Press <Enter> to return...')
            return
    subprocess.run(r'Tools\unpack_report\start_unpack.bat', shell=False)
    print()
    try:
        with open('config.json', 'r', encoding='utf8') as file:
            json_obj = json.load(file)
    except FileNotFoundError:
        logger.error('config.json has not been found in work dir!!!')
        input('Press <Enter> to return...')
        return
    paths_list = db_way(json_obj)
    info_from_reporter = find_info_in_reporter()

    if info_from_reporter:
        print('----------------------------')
        print('  REPORTER INFO:')
        print_func('Trial end date:        None', info_from_reporter['trial_date'])
        print_func('Registry marker:       None', info_from_reporter['registry_marker'])
        print_func('Dongle marker:         None', info_from_reporter['dongle_marker'])
        print(f'Registry UID:          {info_from_reporter["registry_uid"]}')
        print_func('SCCFM version:         None', info_from_reporter['sccfm_version'])
        print_func('RTC UNC clock time:    None', info_from_reporter['rtc_unc'])
        print_func('HOST UNC clock time:   None', info_from_reporter['host_unc'])
        print(f'Dongle UID:            {info_from_reporter["dongle_uid"]}')

        inp = input('Press <Enter> to find UID in database')
        if inp == '':
            if info_from_reporter['registry_uid'] and info_from_reporter['dongle_uid']:
                if info_from_reporter['registry_uid'] == info_from_reporter['dongle_uid']:
                    list_paths_in_db = find_uid_in_db(paths_list, info_from_reporter['dongle_uid'])
                else:
                    logger.warning('Dongle UID is not equal registry UID !!!')
                    input('Press <Enter> to return...')
                    return
            else:
                if info_from_reporter['dongle_uid']:
                    list_paths_in_db = find_uid_in_db(paths_list, info_from_reporter['dongle_uid'])
                elif info_from_reporter['registry_uid']:
                    list_paths_in_db = find_uid_in_db(paths_list, info_from_reporter['registry_uid'])
                else:
                    logger.warning('None UID has been found in ReportDir/reporter.log')
                    input('Press <Enter> to return...')
                    return

            if list_paths_in_db:
                print('  FOUND PATHS:')
                pprint(list_paths_in_db)
                inp = input('Press <Enter> to copy files to work dir')
                if inp == '':
                    if len(list_paths_in_db) == 1:
                        abs_path = os.path.abspath(list_paths_in_db[0]).split(r'Cinema.xml')[0]
                        copy_file(os.path.join(abs_path, r'Cinema.xml'), 'Cinema.xml')
                        copy_file(os.path.join(abs_path, r'CinemaSettings.xml'), 'CinemaSettings.xml')
                    else:
                        logger.warning('More than one UID exists in database')
                        logger.warning('Xmls have not been copied to the work dir')
                        return
                else:
                    logger.info('Copying files has been skipped')
                inp = input('Press <Enter> to go path')
                if inp == '':
                    for path in list_paths_in_db:
                        go_path(path)
                else:
                    logger.info('The transition has been skipped')
        else:
            logger.info('Finding UID has been skipped')
    else:
        input('Press <Enter> to return...')





