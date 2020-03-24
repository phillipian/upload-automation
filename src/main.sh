# repo should be on both on a local machine and the server
# script must be run from a dir with token.pickle present for ssh to go through
# IMPORTANT: server_article_homedir = '/home/plipdigital/temp_articles/' must be empty before running

URL=$1
DATE=$2
SECTIONS='arts'
python local/local_preprocess.py --url $URL --date $DATE --sections $SECTIONS
ssh plipdigital@phillipian.net "cd upload-automation/src/remote; python remote_upload.py --sections $SECTIONS" 
