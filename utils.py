import subprocess

def fix_emails():
    user_command = 'wp user list --role=author --field=ID'
    user_id_list = subprocess.check_output(user_command, shell=True)


def fix_jeffreys_life():
    raise NotImplementedError