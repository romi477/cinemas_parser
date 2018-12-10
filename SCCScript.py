import os
import logging
from datetime import datetime
from unpack_report import main_find_uid
from ips_creator import main_ips_creator
from create_activ_stat import main_create_activstat


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
formatter2 = logging.Formatter('[%(asctime)s %(levelname)s] %(message)s', '%d/%m/%Y %H:%M:%S')

ch1.setFormatter(formatter1)
ch2.setFormatter(formatter2)
logger.addHandler(ch1)
logger.addHandler(ch2)


def main():
    logger.debug('--- Main log has been started ---')

    while True:
        print("""
        1. Unpack SCC2report and find UID in database
        2. Create IPS
        3. Create statistics and activation
        4. Quit
              """)
        choice = input('your choice: ')
        if choice == '1':
            logger.debug('-- unpack-report has been started')
            main_find_uid()
            logger.debug('-- unpack-report has been stopped')
            print('----------------------------')
            print('----------------------------')

        elif choice == '2':
            logger.debug('-- create-ips has been started')
            main_ips_creator()
            logger.debug('-- create-ips has been stopped')
            print('----------------------------')
            print('----------------------------')

        elif choice == '3':
            logger.debug('-- activ-stat has been started')
            main_create_activstat()
            logger.debug('-- activ-stat has been stopped')
            print('----------------------------')
            print('----------------------------')

        elif choice == '4':
            logger.info('Quit')
            break

        else:
            logger.error('Incorrect input, try again')
            print('----------------------------')

    logger.debug('--- Main log has been stoped ---\n')

if __name__ == '__main__':
    main()

