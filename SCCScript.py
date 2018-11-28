import os
import logging
from datetime import datetime
from findUID import main_find_uid
from ipscreator import main_ips_creator
from createActivStart import main_create_activstat


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
    logger.debug('--- Main log start ---')

    while True:
        print("""
        1. Create statistics and activation
        2. Find UID from SCC2report.pack in database
        3. Create IPS.exe
        4. Quit
              """)
        choice = input('your choice: ')

        if choice == '1':
            logger.debug('- activ_stat log stop ---')
            main_create_activstat()
            logger.debug('- activ_stat log stop -')
        elif choice == '2':
            logger.debug('- find_uid log start -')
            main_find_uid()
            logger.debug('- find_uid log stop -')
        elif choice == '3':
            logger.debug('- ips_creator log start -')
            main_ips_creator()
            logger.debug('- ips_creator log stop -')
        elif choice == '4':
            logger.info('Quit')
            break
        else:
            logger.error('incorrect input, try again')
            print('************************************')

    logger.debug('--- Main log stop ---\n')

if __name__ == '__main__':
    main()

