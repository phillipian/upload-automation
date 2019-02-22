import os
from subprocess import call

# cd to wordpress
call("pwd")
os.chdir("/Applications/MAMP/htdocs/wordpress/wp-includes")
call("pwd")

# make a post with the given parameters
call("wp post create --from-post=1 --post_title='Testing wp cli FROM PYTHON'", shell=True)






# fetch articles and photos from sheet
# fetch content
# create posts
# add photos
