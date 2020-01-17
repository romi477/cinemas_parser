import os
import logging
from xml.dom import minidom
from utils import db_way, copy_file
from utils import go_path
from tqdm import tqdm


logger = logging.getLogger('sccscript.findownerpassword')


def compare_attr(attr, value):
    if attr == value:
        return True


def get_attr(xml_obj, name):
    attr = xml_obj.getElementsByTagName(name)
    if attr:
        return attr[0].getAttribute("Value"), name


def parse_cinema_xml(cinema, inp):
    parse_xml = minidom.parse(cinema)
    parse_xml.normalize()
    owner, key = get_attr(parse_xml, "Owner") or get_attr(parse_xml, "OwnerPassword")
    if compare_attr(owner, inp):
        return key, os.path.dirname(cinema)


def input_owner_password():
    while True:
        arg = input("enter owner password: ").strip()
        print()
        if arg == "":
            return
        elif len(arg) != 5:
            logger.info("Owner password must have an 5 digits, try again..")
            print()
            continue
        return arg


def main_find_password(config):
    inp = input_owner_password()
    if not inp:
        return
    paths_list = db_way(config)
    print()
    logger.info(f'Finding {inp} in database, please wait...')
    print()
    count = 0
    found_path = None
    for path in tqdm(paths_list, ncols=74):
        result = parse_cinema_xml(path, inp)
        if not result:
            continue
        else:
            key, found_path = result
            print(f"\n\n{key}: {inp}\nPath: {os.path.abspath(found_path)}\n\n")
            count += 1

    if count == 0:
        logger.info(f"There is no owner password <{inp}> in database!")
        logger.info('Press <Enter> to return...')
        input()

    elif count == 1:
        choice = input("Press <Enter> to copy files to the work dir")
        if choice == '':
            copy_file(os.path.join(found_path, r'Cinema.xml'), 'Cinema.xml')
            copy_file(os.path.join(found_path, r'CinemaSettings.xml'), 'CinemaSettings.xml')
        else:
            logger.info('Copying files has been skipped')

        choice = input('Press <Enter> to follow the path')
        if choice == '':
            go_path(found_path)
    else:
        logger.info('More than one owner password has been found in database!')
        logger.info('Press <Enter> to return...')
        input()



