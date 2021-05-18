# Sync folders
import shutil
import os
import filecmp
from langdetect import detect
import sys

# GLOBAL VARIABLES:
setup_fp = r'D:\ProgramFiles\sync_conf\src_dst_setup.txt'  # The file which contains sources and destinations for sync
will_be_created = []  # A list of files that are on the source but not on the destination: [[src1, dst1], [src2, dst2]...]
will_be_deleted = []  # A list of files that are on the destination but not on the source, and the source is newer: [fp1, fp2...]
will_be_replaced = []  # A list of files that are not updated in the destination, and will be recreated from the source: [[src1, dst1], [src2, dst2]...]
Outdated_source = []  # A list of files that are newer on the destination than on the source, and won't be replaced: [[dst1, src1], [dst2, src2]...]
in_interpreter = False  # Is the program being launched from pycharm of the interpreter


# GENERAL FUNCTIONS:

def conf_shit(printed_path) -> str:
    """
    Formats the str for the interpreter so it will be printed normally (important for hebrew)
    :param printed_path: The str that needs to be formatted
    :return: The formatted str
    """
    if not in_interpreter:
        return printed_path
    new_path = ''
    for word in printed_path.split('\\'):
        if (not word.isnumeric()) and detect(word) == 'he':
            if '.' not in word:
                new_path += f'{word[::-1]}\\'

            else:
                sub_words = word.split('.')
                if (not sub_words[0].isnumeric()) and detect(sub_words[0]) == 'he':
                    new_path += f'{sub_words[0][::-1]}.{sub_words[1]}'
                else:
                    new_path += f'{sub_words[0]}.{sub_words[1]}'
        else:
            new_path += f'{word}\\'
    if new_path[len(new_path) - 1] == '\\':
        new_path = new_path[:-1]
    return new_path


def create_setup() -> None:
    """
    Creates the setup (the user enters sources and destinations, which are being saved in the setup file)
    :return: None
    """
    with open(setup_fp, 'w', encoding='UTF-8') as setup_f:
        setup_f.truncate(0)
        print('Syntax is: {source} | {destination} (for example "D:\src\sub_src | C:\dst\sub_dst")\n'
              'Enter every new source & destination in a new line, press ENTER 2 times when you finish.')
        ans = '-'
        while ans != '':
            ans = input()
            while len(ans.split(' | ')) != 2 and ans != '':
                ans = input('Bruh what the fuck, enter real shit please:\n')
            if ans != '':
                setup_f.write(ans)
                setup_f.write('\n')


def check_if_identical(fp1: str, fp2: str) -> bool:
    """
    Checks if two files are identical or not.
    :param fp1: First file path
    :param fp2: Second file path
    :return: True if they are identical, False if not
    """
    if fp1 == fp2:
        return True
    type_f1 = os.path.splitext(fp1)[-1].lower()
    type_f2 = os.path.splitext(fp2)[-1].lower()

    if type_f1 != type_f2:
        return False
    return filecmp.cmp(fp1, fp2)


def print_setup() -> None:
    """
    Prints the setup from the setup file
    :return: None
    """
    print('Setup is:')
    with open(setup_fp, 'r', encoding='UTF-8') as setup_f:
        dps = setup_f.read().split('\n')
        for line in dps:
            if line != '':
                line = line.split(' | ')
                if len(line) == 2:
                    print(f'src: ~~~~~~~~~ {conf_shit(line[0])} dst: ~~~~~~~~~ {conf_shit(line[1])}')


def print_sync() -> None:
    """
    Prints all the lists of files for the user to check and make sure it's ok
    :return: None
    """
    print('===========================================================================================================')
    if len(will_be_created) > 0:
        print('Going to be created:')
        for i, (src, dst) in enumerate(will_be_created):
            if os.path.isdir(src):
                print(i, 'New (directory) -------------------------------------', conf_shit(dst))
                print(i, 'From (directory) ------------------------------------', conf_shit(src))
            else:
                print(i, 'New (file) ------------------------------------------', conf_shit(dst))
                print(i, 'From (file) -----------------------------------------', conf_shit(src))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    if will_be_deleted != []:
        print('Going to be deleted:')
        for i, something in enumerate(will_be_deleted):
            if os.path.isdir(something):
                print(i, 'Delete (directory) -----------------------------------', conf_shit(something))
            else:
                print(i, 'Delete (file) ----------------------------------------', conf_shit(something))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    if will_be_replaced != []:
        print('Going to be replaced:')
        for i, (src_fp, dst_fp) in enumerate(will_be_replaced):
            print(i, 'Replace (file) ---------------------------------------', conf_shit(dst_fp))
            print(i, 'With (file) ------------------------------------------', conf_shit(src_fp))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    if Outdated_source != []:
        print("Outdated source (the destination is newer, won't be replaced):")
        for i, (dst_fp, src_fp) in enumerate(Outdated_source):
            print(i, 'Newer (file) ------------------------------------------', conf_shit(dst_fp))
            print(i, 'Older (file) ------------------------------------------', conf_shit(src_fp))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')


# ======================================================================================================================
# SIDE FUNCTIONS:

def search_trash(src_dp, dst_dp) -> None:
    """
    Searches for file which are in the destination but not on the source, and adds them to the will_be_deleted list.
    :param src_dp: Source directory path
    :param dst_dp: Destination directory path
    :return: None
    """
    global will_be_deleted
    src_dir = os.listdir(src_dp)
    dst_dir = os.listdir(dst_dp)
    for something in dst_dir:

        if not something in src_dir:
            will_be_deleted.append(os.path.join(dst_dp, something))


def change_created(change: list) -> None:
    """

    :param change:
    :return:
    """
    global will_be_created
    if change[1] > len(will_be_created):
        print("Value doesn't exist...")
    elif will_be_created[change[1]] == '~Canceled~':
        print('It was already canceled...')

    elif input('Do you want to avoid creating this? ([y]/n): ') != 'n':
        place = change[1]
        will_be_created[place][0] = '~Canceled~'
        will_be_created[place][1] = '~Canceled~'


def change_deleted(change: list) -> None:
    """
    Changes the will_be_deleted list according to the user.
    :param change: The list in the will_be_deleted list that needs to be changes.
    :return: None
    """
    if change[1] > len(will_be_deleted):
        print("Value doesn't exist...")

    elif will_be_deleted[change[1]] == '~Canceled~':
        print('It was already canceled...')
    elif input('Do you want to avoid deleting this? ([y]/n): ') != 'n':
        will_be_deleted[change[1]] = '~Canceled~'


def change_replaced(change: list) -> None:
    """
    Changes the will_be_replaced list according to the user.
    :param change: The list in the will_be_replaced list that needs to be changes.
    :return: None
    """
    global will_be_replaced
    if change[1] > len(will_be_replaced):
        print("Value doesn't exist...")
    else:
        place = change[1]

        if will_be_replaced[place][0] == '~Canceled~':
            print('It was already canceled...')
        elif input('Do you want to avoid replacing? (y/[n]): ') == 'y':
            will_be_replaced[place][0] = '~Canceled~'
            will_be_replaced[place][1] = '~Canceled~'
        elif input('Do you want to replace the other way? (y/[n]): ') == 'y':
            new_src = will_be_replaced[place][1]
            will_be_replaced[place][1] = will_be_replaced[place][0]
            will_be_replaced[place][0] = new_src


def change_outdated(change: list) -> None:
    """
    Changes the outdated_source list according to the user (may add it to will_be_replaced).
    :param change: The list in the outdated_source list that needs to be changes.
    :return: None
    """
    global Outdated_source
    if change[1] > len(Outdated_source):
        print("Value doesn't exist...")
    else:
        place = change[1]

        if Outdated_source[place][0] == '~Canceled~':
            print('It was already canceled...')

        elif input('Do you want to replace anyway? (y/[n]): ') == 'y':
            will_be_replaced.append([Outdated_source[place][1], Outdated_source[place][0]])
            Outdated_source[place][0] = '~Canceled~'
            Outdated_source[place][1] = '~Canceled~'


def change_something() -> None:
    """
    If the user wants to change something after going over the lists.
    :return: None
    """
    change = (len(will_be_created) > 0 or len(will_be_deleted) > 0 or len(will_be_replaced) > 0 or len(
        Outdated_source) > 0) and input(
        'Do you want to change something? ([y]/n): ') != 'n'
    menu = 'Changing menu:\n-> n for new\n-> d for delete\n-> r for replace\n-> o for outdated source\n-> m for ' \
           'menu\nFor example, "r 1" - replace 1.'
    if change:
        print(menu)

    while change:
        change = input('Enter n/d/r/o/m (number) according to what you want to change: ')
        change = change.split(' ')

        if type(change) == list and len(change) == 2 and change[1].isnumeric():

            change[1] = int(change[1])

            if change[0] == 'n':
                change_created(change)

            if change[0] == 'd':
                change_deleted(change)

            elif change[0] == 'r':
                change_replaced(change)

            elif change[0] == 'o':
                change_outdated(change)

            else:
                print(menu)

        elif change == ['m']:
            print(menu)
        else:
            print("Can't find '", str(change), "'", sep='')
        print_sync()
        change = input('Do you want to change something else? ([y]/n): ') != 'n'


def sync_file(src_fp: str, src_fn: str, dst_dp: str) -> None:
    """
    Adding file to "will_be_replaced", "will_be_deleted" or "will_be_created"
    :param src_fp: Source file path
    :param src_fn: Source file name
    :param dst_dp: Destination directory path
    :return: None
    """
    dst_dir = os.listdir(dst_dp)
    dst_fn = src_fn
    if src_fn in dst_dir:
        dst_fp = os.path.join(dst_dp, dst_fn)
        if not check_if_identical(src_fp, dst_fp):

            if os.stat(dst_fp).st_mtime > os.stat(src_fp).st_mtime:
                global Outdated_source
                Outdated_source.append([dst_fp, src_fp])
            else:
                global will_be_replaced
                will_be_replaced.append([src_fp, dst_fp])
    else:
        global will_be_created
        will_be_created.append([src_fp, os.path.join(dst_dp, src_fn)])


# ======================================================================================================================
# MAIN SHIT:

def use_setup() -> None:
    """
    Syncing directories according to the sync setup file (located in the setup_fp path)
    :return: None
    """
    with open(setup_fp, 'r', encoding='UTF-8') as setup_f:
        dps = setup_f.read().split('\n')
        for line in dps:
            if line != '':
                line = line.split(' | ')
                src_dp = line[0]
                dst_dp = line[1]
                if os.path.exists(src_dp) and os.path.isdir(src_dp) and os.path.exists(dst_dp) and os.path.isdir(
                        dst_dp):
                    sync_directory(src_dp, dst_dp)
                else:
                    print(f'{conf_shit(src_dp)} or {conf_shit(dst_dp)} does not exist/not a directory.')


def sync_directory(src_dp: str, dst_dp: str) -> None:
    """
    Goes over every file in the destination tree, creates it if it doesn't exist and syncs it if in does.
    :param src_dp: source directory path
    :param dst_dp: destination directory path
    :return: None
    """
    src_dir = os.listdir(src_dp)
    search_trash(src_dp, dst_dp)

    for i in range(len(src_dir)):
        src_dir = os.listdir(src_dp)
        dst_dir = os.listdir(dst_dp)

        if os.path.isdir(f'{src_dp}\\{src_dir[i]}'):  # If src_dir[i] is a directory

            if not src_dir[i] in dst_dir:  # If the directory isn't in the dst_dir
                global will_be_created
                will_be_created.append([os.path.join(src_dp, src_dir[i]), os.path.join(dst_dp, src_dir[i])])

            else:
                src_sub_dir = os.path.join(src_dp, src_dir[i])
                dst_sub_dir = os.path.join(dst_dp, src_dir[i])
                sync_directory(src_sub_dir, dst_sub_dir)
        else:
            src_fp = os.path.join(src_dp, src_dir[i])
            sync_file(src_fp, src_dir[i], dst_dp)


def finale_sync() -> None:
    """
    Deleting/replacing files according to the global "trash", "replace" and "newer_in_dst" lists
    :return: None
    """
    global will_be_created
    global will_be_deleted
    global will_be_replaced
    global Outdated_source

    for src, dst in will_be_created:
        if src != '~Canceled~':
            if os.path.isdir(src):
                print('New (directory) --------------------------------------', conf_shit(dst))
                print('From (directory) -------------------------------------', conf_shit(src))
                os.mkdir(dst)
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                print('New (file) -------------------------------------------', conf_shit(dst))
                print('From (file) ------------------------------------------', conf_shit(src))
                shutil.copy(src, dst)

    for something in will_be_deleted:
        if something != '~Canceled~':
            if os.path.isdir(something):
                print('Delete (directory) -----------------------------------', conf_shit(something))
                shutil.rmtree(something)
            else:
                print('Delete (file) ----------------------------------------', conf_shit(something))
                os.remove(something)

    for src_fp, dst_fp in will_be_replaced:
        if src_fp != '~Canceled~':
            print('Replace (file) ---------------------------------------', conf_shit(dst_fp))
            print('With (file) ------------------------------------------', conf_shit(src_fp))
            dst_dp = os.path.split(dst_fp)[0]
            os.remove(dst_fp)
            shutil.copy(src_fp, dst_dp)


def setup() -> None:
    """
    Makes sure the setup file exists and fine with the user
    """
    global in_interpreter
    global setup_fp

    in_interpreter = input('Are you in the shell interpreter? ([y]/n): ') != 'n'
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1]):
        setup_fp = sys.argv[1]
    if not os.path.exists(setup_fp):
        create_setup()
    print_setup()
    while input('Fine? ([y]/n): ') == 'n':
        create_setup()
        print_setup()


# ======================================================================================================================
if __name__ == '__main__':
    setup()

    use_setup()
    print_sync()
    change_something()
    finale_sync()
    input('Sync was successful! Press enter to exit')
