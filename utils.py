import os
import subprocess
from student_directory import StudentDirectory
import json

os.chdir('/home/plipdigital/phillipian.net') # must run script in wordpress installation, so cd

def fix_emails():
    '''
    Usage: properly assign Andover emails to author accounts that don't have legit emails
    '''
    with open('../students.json', 'r') as f:
        students = json.load(f)
    directory = StudentDirectory(students)

    user_command = 'wp user list --role=author --fields=ID'
    user_id_list = subprocess.check_output(user_command, shell=True).split('\n')
    name_list = subprocess.check_output('wp user list --role=author --fields=display_name', shell=True).split('\n')
    info_list = zip(user_id_list, name_list)
    for user in info_list[1:]: #loop through but skip first element in list bc it's not valid from zip
        email_command = 'wp user get {} --field=email'.format(user[0])
        email = subprocess.check_output(email_command, shell=True)
        if '@andover.edu' in email:
             continue
        elif 'and' in email:
             continue
        elif ' ' not in user[1]:
             continue
        full_name = user[1]
        first_name = user[1].split(' ')[0]
        last_name = user[1].split(' ')[1]
        print(first_name)
        try:
            new_email = directory.student_dict[directory.search_by_name(first_name, last_name)[0]]['email']
            update = 'wp user update {} --user_email={}'.format(user[0], new_email)
            subprocess.call(update, shell=True)
            print('Successfully added email {} to user {}'.format(new_email, full_name))
        except:
            continue

def fix_authors():
    '''
    Usage: deal with previous "and" authors that are now bad
    '''
    user_command = 'wp user list --role=author --fields=ID'
    user_id_list = subprocess.check_output(user_command, shell=True).split('\n')
    name_list = subprocess.check_output('wp user list --role=author --fields=display_name', shell=True).split('\n')
    info_list = zip(user_id_list, name_list)
    print(info_list)

def fix_jeffreys_life():
    raise NotImplementedError


