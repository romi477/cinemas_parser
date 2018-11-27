import subprocess
import sys
import os
import json
import re
import shutil
import glob


def get_unpack(proc1, proc2):
    code1 = subprocess.run(proc1, shell=False)
    if code1.returncode == 0:
        try:
            code2 = subprocess.run(proc2, shell=False)
        except FileNotFoundError:
            print('WARNING: systeminfo.xmlb.xml was not created')
        print('INFO: SCC2Report.pak was unpaked, please wait...')
    else:
        print('ERROR: the archive was not unpacked...')
        sys.exit(1)

def find_uid():
    try:
        with open(r'reportDir\reporter.log', 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print('ERROR: reporter.log not found...')
        input('press <Enter> to exit...')
        sys.exit(1)

    for line in lines:
        str_uid = re.search(r'\w\w\w\w\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w-\w\w\w\w\w\w\w\w\w\w\w\w', line)
        if str_uid:
            str_split = line.split('\t')[1].split(':')
            dic = {'uid': str_uid.group(0), 'from': str_split[0].strip()}
            return dic
    print('WARNING: sorry, there is not UID in reporter.log ...')
    input('press <Enter> to exit...')
    sys.exit(1)

def db_way():
    with open('config.json', 'r', encoding='utf8') as file:
        json_obj = json.load(file)

    return glob.glob(json_obj['path'], recursive=True)

def get_compare(lst, uid):
    point = 0
    for ls in lst:
        if lst.index(ls) % 30 == 0 or point == 0:
            point += 1
            sys.stdout.write(f"\r{point * '.'}")
            sys.stdout.flush()
        with open(ls, 'r') as file:
            read_obj = file.read()
        uid_tmp = re.search(uid, read_obj)
        if uid_tmp:
            return ls
    return False

def go_path(path):
    abs_path = os.path.abspath(path)
    abs_path = abs_path.split(r'\Cinema.xml')[0]
    proc = r'explorer.exe /n, {}'.format(abs_path)
    event = subprocess.run(proc, shell=True)


def main_find_uid():
    proc1 = r'Tools\find_uid\Compressor.exe unpack SCC2Report.pak reportDir'
    proc2 = r'Tools\find_uid\XMLB2XML.exe reportDir\systeminfo.xmlb'
    try:
        print('<reportDir> is deleting, please wait!')
        shutil.rmtree('reportDir')
        print('ok, here we go!')
    except:
        pass
    get_unpack(proc1, proc2)
    report_data = find_uid()
    lst_paths = db_way()
    ls_path = get_compare(lst_paths, report_data['uid'])
    if ls_path:
        print('', f'UID <{report_data["uid"]}> was found in <{report_data["from"]}>', ls_path, sep='\n')
        print()
        input('press <Enter> to go...')
        go_path(ls_path)
    else:
        print('', f'WARNING: UID <{report_data["uid"]}> not found in database...', sep='\n')
        input('press <Enter> to exit...')
