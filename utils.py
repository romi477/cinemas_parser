from re import fullmatch
import subprocess
import shutil
import logging


logger = logging.getLogger('sccscript.utils')

def check_input_date(func):
    def wrapper(*args, **kwargs):
        if kwargs['inp_date']:
            if fullmatch(r'\d\d\d\d\d\d', kwargs['inp_date']):
                return func(*args, **kwargs)
            else:
                logger.error(f'Enter {kwargs["key"]} date as <%d%m%y>, for example: 010199,\n'
                              'or press <Enter> to set default date ...')
                print('----------------------------\n')
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
        input('Press <Enter> to return...')
    except IOError:
        logger.error(f'{get_file} has not been copied')
        input('Press <Enter> to return...')
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
            input('press <Enter> to return...')
    else:
        logger.error(f'{cmd} - FAIL')
        input('Press <Enter> to return...')

