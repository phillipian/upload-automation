# repo should be on both on a local machine and the server
# script must be run from a dir with token.pickle present for ssh to go through
# IMPORTANT: server_article_homedir = '/home/plipdigital/temp_articles/' must be empty before running

URL=''
DATE=''
SECTIONS=''
python local_preprocess.py --url $URL --date $DATE --sections $SECTIONS
ssh plipdigital@phillipian.net 
python remote_upload.py --sections $SECTIONS
