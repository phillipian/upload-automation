server_name = 'plipdigital@phillipian.net/home/plipdigital/phillipian.net' 

# PATHS
# local
local_article_path = '../articles/'
local_img_path = '/Users/jzpan/digital/' # TODO: path to photos in the docker image / local computer
# server
server_article_homedir = '/home/plipdigital/temp_articles/' # path to article dir/.. on the server
server_article_path = server_article_homedir+local_article_path # path to articles on the server 
wp_install_dir = '/home/plipdigital/phillipian.net' # location to run remote upload script
server_img_path = '/home/plipdigital/wp-photos/' # path to photos on the server, should contain date folders

# CONTENT
NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage', 'Multilingual':'multilingual', 'Editorial':'editorial'}
