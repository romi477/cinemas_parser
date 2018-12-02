import subprocess
import os
import json
import re
import shutil
import glob
import logging
# from msvcrt import getch


logger = logging.getLogger('sccscript.unpackreport')

def find_uid_in_reportdir():
    try:
        with open(r'ReportDir\reporter.log', 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        logger.error('ERROR: reporter.log not found')
        return

    dict_uid = {}
    for line in lines:
        str_uid = re.search(r'\w\w\w\w\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w\w\w\w\w\w\w\w\w', line)
        if str_uid:
            logger.info(line.split(']')[-1].strip())
            if 'Instance' in line:
                dict_uid['registry'] = str_uid.group(0)
            elif 'dongle' in line:
                dict_uid['dongle'] = str_uid.group(0)
    return dict_uid

def db_way(json_obj):
    iter_paths = glob.iglob(json_obj['path'], recursive=True)
    return [path for path in iter_paths if 'old' not in path]

def find_uid_in_db(lst, uid):
    logger.info('Searching UID in database, please wait...')
    list_from_db = []
    for ls in lst:
        with open(ls, 'r') as file:
            read_obj = file.read()
        uid_tmp = re.search(uid, read_obj)
        if uid_tmp:
            list_from_db.append(ls)
            logger.info(f'[ {ls} ]' + ' was found in database')
    return list_from_db

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
        logger.error('Cinema.xml was not copied in work dir')
        return
    try:
        shutil.copy2(os.path.join(abs_path, r'CinemaSettings.xml'), 'CinemaSettings.xml')
    except IOError:
        logger.error('CinemaSettings.xml was not copied in work dir')
        return
    logger.info('Cinema.xml was copied in work dir')
    logger.info('CinemaSettings.xml was copied in work dir')

def main_find_uid():
    if os.path.exists('ReportDir'):
        logger.info('<ReportDir> is deleting, please wait...')
        shutil.rmtree('ReportDir')

    subprocess.run(r'Tools\unpack_report\start_unpack.bat', shell=False)

    try:
        with open('config.json', 'r', encoding='utf8') as file:
            json_obj = json.load(file)
    except FileNotFoundError:
        logger.error('config.json not found in work dir!!!')
        return

    lst_paths = db_way(json_obj)
    uid_from_reporter = find_uid_in_reportdir()

    if uid_from_reporter:
        if 'dongle' in uid_from_reporter.keys() and 'registry' in uid_from_reporter.keys():
            if uid_from_reporter['dongle'] == uid_from_reporter['registry']:
                list_paths_in_db = find_uid_in_db(lst_paths, uid_from_reporter['dongle'])
            else:
                logger.warning('Dongle UID is not equal UID from registry!!!')
                input('press <Enter> to return...')
                return
        else:
            list_paths_in_db = find_uid_in_db(
                lst_paths,
                uid_from_reporter.get('dongle', uid_from_reporter.get('registry'))
            )
    else:
        input('press <Enter> to return...')
        return

    if len(list_paths_in_db) == 1:
        copy_cinema_to_workdir(list_paths_in_db[0])
        key = input('press <Enter>/<other key> to go to the cinema dir, or not :')
        if key == '':
            go_path(list_paths_in_db[0])
        else:
            return
    else:
        logger.warning('More then one UID exist in database')
        input('press <Enter> to return...')
        return

