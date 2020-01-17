import os
import glob
import shutil
import logging
import subprocess
from re import search
from tqdm import tqdm
from re import fullmatch


logger = logging.getLogger('sccscript.utils')


def go_path(path):
    proc = r'explorer.exe /n, {}'.format(path)
    subprocess.run(proc, shell=True)


def check_input_date(func):
    def wrapper(*args, **kwargs):
        if kwargs['inp_date']:
            if fullmatch(r'\d\d\d\d\d\d', kwargs['inp_date']):
                return func(*args, **kwargs)
            else:
                logger.error(f'Enter {kwargs["key"]} date as <%d%m%y>, for example: 010199,\n'
                              'or press <Enter> to set default date ...')
                print('---------------------------------------\n')
                return
        else:
            logger.debug(f'Default value of {kwargs["key"]} date')
            return kwargs['def_date']
    return wrapper


def endless_cycle(func):
    def wrapper(*args, **kwargs):
        while True:
            result = func(*args, **kwargs)
            if result:
                return result
            else:
                kwargs['inp_date'] = input(f'{kwargs["key"]} date: ')
    return wrapper


def copy_file(get_file, set_file):
    try:
        shutil.copy2(get_file, set_file)
    except FileNotFoundError:
        logger.error(f'{get_file} has not been found')
        logger.info('Press <Enter> to return...')
        input()
    except IOError:
        logger.error(f'{get_file} has not been copied')
        logger.info('Press <Enter> to return...')
        input()
    else:
        logger.info(f'{get_file}\n       has been copied to the work dir as {set_file}')
        return True


def sign_compress(cmd, compress):
    sign = subprocess.run(cmd, shell=False)
    if sign.returncode == 0:
        logger.info(f'{cmd} - OK')
        code = subprocess.run(compress, shell=False)
        if code.returncode == 0:
            logger.info(f'{compress} - OK')
        else:
            logger.error(f'{compress} - FAIL')
            logger.info('Press <Enter> to return...')
            input()
    else:
        logger.error(f'{cmd} - FAIL')
        logger.info('Press <Enter> to return...')
        input()


def db_way(config):
    iter_list = config['db_path'] + '\\*\\*\\**\\Cinema.xml'
    iter_paths = glob.iglob(iter_list, recursive=True)
    return [path for path in iter_paths if os.path.sep + 'old' not in path]


def find_string_in_db(paths_list, a_string):
    logger.info(f'Finding "{a_string}" in database, please wait...')
    uid_list_from_db = []
    for path in tqdm(paths_list, ncols=74):
        with open(path, 'r') as file:
            read_obj = file.read()
        uid_tmp = search(a_string, read_obj)
        if uid_tmp:
            uid_list_from_db.append(os.path.abspath(path))
    return uid_list_from_db

