import os
import glob
import shutil
import logging
import pyexcel
import subprocess
from re import search
from xml.dom import minidom
import xml.etree.ElementTree as ET
from utils import db_way, copy_file, find_string_in_db, go_path


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
        uid = search(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12}', line)
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


def print_dict(dct):

    print('---------------------------------------')
    print(f'{"":<16}FOUND PATHS:')
    print()
    for k, v in dct.items():
        print(f'{k}:')
        print('\n'.join(v))
    print('---------------------------------------')


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


def movie_parser(movie_pth):
    root = ET.parse(movie_pth).getroot()
    expired = root.find('Expired')
    try:
        license = expired.get('Value')
        return license
    except AttributeError:
        return None


def walk_pth(pth):
    content_list = []
    iter_movies = glob.glob(pth + r'\\*\\*.xml')
    for idx, movie_pth in enumerate(iter_movies, 1):
        movie_license = movie_parser(movie_pth)
        mps = movie_pth.split(os.path.sep)
        print(f'{"/".join(mps[-3:-1]):<26} {idx}. {mps[-1].split(".")[-2]:<23}{movie_license}')
        content_list.append([f'{"/".join(mps[-3:-1])}', f'{idx}.', f'{mps[-1].split(".")[-2]}', f'{movie_license}'])
    return content_list


def main_find_uid_inner(config):
    if not os.path.exists('ReportDir'):
        print()
        logger.error('<ReportDir> does not exist!')
        logger.info('Make sure that SCC2Report.pak was unpacked in <ReportDir>!')
        logger.info('Press <Enter> to return...')
        input()
        return

    paths_list = db_way(config)
    reporter_dict = find_info_in_reporter()

    if reporter_dict:
        print('---------------------------------------')
        print(f'{"":<16}REPORTER INFO')
        print()
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
                1 - Find UID in database
                2 - Analyze content
                3 - Main menu
                      """)
            choice = input('your choice: ')
            if choice == '1':
                uid_list_from_db = {}
                if reporter_dict['registry_uid'] and reporter_dict['dongle_uid']:
                    if reporter_dict['registry_uid'] == reporter_dict['dongle_uid']:
                        logger.info('Dongle UID is equal Registry UID')
                        uid_list_from_db['Dongle_UID'] = find_string_in_db(paths_list, reporter_dict['dongle_uid'])
                    else:
                        logger.warning('Dongle UID is not equal Registry UID!')
                        uid_list_from_db['Dongle_UID'] = find_string_in_db(paths_list, reporter_dict['dongle_uid'])
                        uid_list_from_db['Registry_UID'] = find_string_in_db(paths_list, reporter_dict['registry_uid'])
                        print_dict(uid_list_from_db)
                        print('---------------------------------------')
                        continue
                else:
                    if reporter_dict['dongle_uid']:
                        logger.warning('Only Dongle UID has been parsed from reporter.log')
                        uid = find_string_in_db(paths_list, reporter_dict['dongle_uid'])
                        if uid:
                            uid_list_from_db['Dongle_UID'] = uid
                    elif reporter_dict['registry_uid']:
                        logger.warning('Only Registry UID has been parsed from reporter.log')
                        uid = find_string_in_db(paths_list, reporter_dict['registry_uid'])
                        if uid:
                            uid_list_from_db['Registry_UID'] = uid
                    else:
                        logger.warning('None of UID has been found in reporter.log')
                        print('---------------------------------------')
                        continue

                if uid_list_from_db:
                    print_dict(uid_list_from_db)
                    try:
                        path_xml = uid_list_from_db['Dongle_UID']
                    except KeyError:
                        path_xml = uid_list_from_db['Registry_UID']
                    if len(path_xml) == 1:
                        abs_path_xml = os.path.abspath(path_xml[0]).split(r'Cinema.xml')[0]
                        choice = input('Press <Enter> to copy files to the work dir')
                        if choice == '':
                            copy_file(os.path.join(abs_path_xml, r'Cinema.xml'), 'Cinema.xml')
                            copy_file(os.path.join(abs_path_xml, r'CinemaSettings.xml'), 'CinemaSettings.xml')
                        else:
                            logger.info('Copying files has been skipped')

                        choice = input('Press <Enter> to follow to the path')
                        if choice == '':
                            go_path(abs_path_xml)
                    else:
                        logger.warning('More than one UID exists in database')
                        print('---------------------------------------')
                        continue
                else:
                    logger.warning('None of the required UID has been found in Database')
                    print('---------------------------------------')
                    continue
                print('---------------------------------------')

            elif choice == '2':
                print('---------------------------------------')
                print(f'{"":<16}CONTENT')
                print()
                full_content_list = []
                for pth in config['content_dirs']:
                    if os.path.exists(pth) and os.listdir(pth):
                        full_content_list.extend(walk_pth(pth))
                print()
                if full_content_list:
                    inp = input('Export content to xls or xml: ')
                    inp = inp.lower().split()
                    if not inp:
                        logger.info('Export has been skipped')
                        return
                    if not os.path.exists('content'):
                        os.mkdir('content')

                    uid = reporter_dict.get('registry_uid')
                    cont_uid = uid if uid else reporter_dict.get('dongle_uid')
                    print()
                    for ext in inp:
                        content_name = f'{cont_uid}.{ext}'
                        if ext == 'xls':
                            try:
                                pyexcel.save_as(array=full_content_list, dest_file_name=os.path.join("content", f'content-{content_name}'))
                                logger.info(f'File content/content-{content_name} has been successfully created')
                            except Exception as ex:
                                logger.error(ex)
                                raise

                        elif ext == 'xml':
                            root = ET.Element('Cinema')
                            root.set('TrackType', '2dof')
                            root.set('Resolution', '...')
                            root.set('Language', '...')

                            content = ET.Element('Content')
                            root.append(content)

                            for record in full_content_list:
                                movie = ET.SubElement(content, 'Movie')
                                movie.set('Title', record[2])
                                try:
                                    movie.set('Licensed', record[3])
                                except IndexError:
                                    movie.set('Licensed', None)

                            root_string = ET.tostring(root, encoding="unicode", method="xml")
                            dom = minidom.parseString(root_string)
                            dom.normalize()

                            try:
                                with open(os.path.join("content", f'template-{content_name}'), 'w') as file:
                                    dom.writexml(file, addindent=" " * 4, newl="\n")
                                logger.info(f'File content/template-{content_name} has been successfully created')
                            except Exception as ex:
                                logger.error(ex)
                                raise

                        else:
                            logger.info(f'Incorrect extension *.{ext}')
                else:
                    logger.warning('Content has not been found')
                print('---------------------------------------')

            elif choice == '3':
                break
    else:
        logger.warning('<Reporter info> has not been parsed')


def main_find_uid(config):
    if os.path.exists('ReportDir'):
        logger.info('<ReportDir> is being deleted, please wait...')
        try:
            shutil.rmtree('ReportDir')
        except Exception as e:
            logger.error(e)
            logger.error('Rename the directory <Reportdir> and try again')
            logger.info('Press <Enter> to return...')
            input()
            return
    if not os.path.exists('SCC2Report.pak'):
        print()
        logger.error('<SCC2Report.pak> was not found!')
        logger.info('Press <Enter> to return...')
        input()
        return
    subprocess.run(r'Tools\unpack_report\start_unpack.bat')
    print()
    main_find_uid_inner(config)



