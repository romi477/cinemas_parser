import os
import sys
import json
import msvcrt
import logging
from datetime import datetime
from ips_creator import main_ips_creator
from create_activ_stat import main_create_activstat
from find_owner_password import main_find_password
from unpack_report import main_find_uid, main_find_uid_inner


date = datetime.today()
if not os.path.exists('logs'):
    os.mkdir('logs')
pth = f'logs\{date.strftime("%m-%Y")}'
if not os.path.exists(pth):
    os.mkdir(pth)

logger = logging.getLogger('sccscript')
logger.setLevel(logging.DEBUG)

ch1 = logging.StreamHandler()
ch1.setLevel(logging.INFO)
ch2 = logging.FileHandler(filename=pth + f'\{date.strftime("%d-%m-%Y")}.log', delay=False)
ch2.setLevel(logging.DEBUG)

formatter1 = logging.Formatter('[%(levelname)s] %(message)s')
formatter2 = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', '%d/%m/%Y %H:%M:%S')

ch1.setFormatter(formatter1)
ch2.setFormatter(formatter2)
logger.addHandler(ch1)
logger.addHandler(ch2)


def main():
    logger.debug('--- Main log has been started ---')

    try:
        with open('config.json', 'r', encoding='utf8') as file:
            config = json.load(file)
    except FileNotFoundError:
        logger.error('config.json has not been loaded!')
        sys.exit(1)

    while True:
        print("""
        1 - Unpack report
        2 - Create IPS
        3 - Create statistics and activation
        
        f - Find device by owner password
        r - Enter via unpacked report
        
        q - Quit
              """)
        choice = input('your choice: ').lower()

        if choice == '1':
            logger.debug('<unpack-report> function has been started')
            main_find_uid(config)
            logger.debug('<unpack-report> has been finished')
            print('----------------------------')
            print('----------------------------')

        elif choice == '2':
            logger.debug('<create-ips> function has been started')
            main_ips_creator()
            logger.debug('<create-ips> has been finished')
            print('----------------------------')
            print('----------------------------')

        elif choice == '3':
            logger.debug('<activ-stat> function has been started')
            main_create_activstat()
            logger.debug('<activ-stat> has been finished')
            print('----------------------------')
            print('----------------------------')

        elif choice == 'r':
            logger.debug('<reported-mod> has been started')
            main_find_uid_inner(config)
            logger.debug('<reported-mod> has been finished')

        elif choice == 'f':
            logger.debug('<find password-mod> has been started')
            print()
            main_find_password(config)
            logger.debug('<find password-mod> has been finished')
            print('----------------------------')
            print('----------------------------')

        elif choice == 'q':
            break

        else:
            logger.error('Incorrect input, try again')
            print('----------------------------')

    logger.debug('--- Main log has been stopped ---\n')
    sys.exit()


if __name__ == '__main__':

    try:
        main()
    except Exception as ex:
        logger.error(ex)
        logger.exception('Fatal error!')
