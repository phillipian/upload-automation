# SERVER
wp_install_dir = '/home/plipdigital/phillipian.net'
server_name = 'plipdigital@phillipian.net/home/plipdigital/phillipian.net' 

# CONSTANTS
local_article_path = 'articles/'
server_article_homedir = '/home/plipdigital/temp_articles/' # path to articles on the server
# path to articles on the server (same as from local script + articles/)
server_article_path = server_article_homedir+local_article_path


# IMG CONSTANTS
local_img_path = '/Users/jzpan/digital/' # TODO: path to photos in the docker image / local computer
server_img_path = '/home/plipdigital/wp-photos/' # path to photos on the server, should contain date folders

NOPHOTO = 'nophoto'
special_photo_credits = ['Archives', 'Courtesy of ']
category_slugs = {'Arts':'arts', 'Commentary':'commentary', 'Editorial':'editorial', 'Featured Posts':'featured', 'News':'news', 'Sports':'sports', 'The Eighth Page':'eighthpage', 'Multilingual':'multilingual', 'Editorial':'editorial'}
