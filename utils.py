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
    #user_command = 'wp user list --role=author --fields=ID'
    #user_id_list = subprocess.check_output(user_command, shell=True).split('\n')
    name_list = subprocess.check_output('wp user list --role=author --fields=display_name', shell=True).split('\n')
    #info_list = zip(user_id_list, name_list)
    fix_name_list = []
    for user in name_list:
        first_user = None
        second_user = None
        if ' and ' in user.lower():
            first_user = user.split(' and ')[0]
            second_user = user.split(' and ')[1]

        elif ' Translated by ' in user:
            first_user = user.split(' Translated by ')[0]
            second_user = user.split(' Translated by ')[1]
        else:
           
            continue
        if first_user not in fix_name_list and first_user not in name_list:
            fix_name_list.append(first_user)
        if second_user not in fix_name_list and second_user not in name_list:
            fix_name_list.append(second_user)
    print(fix_name_list)
     
def fix_posts():
    '''
    Usage: reassign posts from broken author usernames with ands to their respective authors
    '''
    fix_post_list = []

    post_id_list = subprocess.check_output('wp post list --field=ID', shell=True).split('\n') 

    for post_id in post_id_list:
        author = subprocess.check_output('wp post get {} --field=post_author'.format(post_id), shell=True).strip()
        author_name = subprocess.check_output('wp user get {} --field=display_name'.format(author), shell=True)).strip()
        if 'The Phillipian' in author_name:
            continue
        if ' and ' in author_name:
            author_one = author_name.split(' and ')[0]
            author_two = author_name.split(' and ')[1]
        elif ', ' in author_name:
            author_one = author_name.split(', ')[0]
            author_two = author_name.split(', ')[1]
        subprocess.call('wp co-authors-plus add-coauthors --coauthor={} --post_id={}'.format(author_one, post_id), shell=True)
        subprocess.call('wp co-authors-plus add-coauthors --coauthor={} --post_id={}'.format(author_two, post_id), shell=True)
        
        

        

fix_posts()

def fix_jeffreys_life():
    raise NotImplementedError


