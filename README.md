# Phillipian Article Upload Automation
Project to automate uploading to phillipian.net
### Structure
upload_script.py is the main script. It will be run from a docker container on a computer in the newsroom to more easily access the photo server.
### Usage
- [ ] Fill out the budget and make sure there are no missing fields (mark articles to upload, add image directory or the no image string to the budget, caption, credit, etc)
- [ ] Add BOF and EOF markers in article docs
- [ ] python upload_script.py --url URL
- [ ] Check ALL posts (and maybe publish them by hand?)
- [ ] Upload editorial manually?
- [ ] Mark categories manually (featured, look of the week, sports season, sports teams), either in the budget ahead of time (we can integrate it into the script) or afterwards
- [ ] Multilingual uploading?
### Jobs
- [ ] Jeffrey - do old author creation and assignment, read and make compatible current code for that and add multiple author functionality (ask Samson for details)
- [ ] Alex - make a docker image with everything needed for easier running, look into how to upload on the **real** website (configging etc)
- [ ] Sarah - add basic category functionality
### Logistical To Do
- [ ] Change config file to access real website
- [ ] Changes to the budget (ESSENTIAL)
  - [ ] Use the headline column (or fill it in at the end)
  - [ ] Add 'Link' column that stores explicit link to document with article on it
  - [ ] Add 'Upload?' column that stores 'yes' or 'no'
  - [ ] Add 'ImageDir' column that stores photo directory
- [ ] Add standardized BOF and EOF file strings in each article's Google Document
### Project Requirements
- [ ] Probably **download budget** from the folder using drive CLI 
- [ ] Extract **article text** from slug column (get from start to page break) also probably using drive CLI
- [ ] Extract **writer, headline, and section** from budget
- [ ] Post to the website us wp post create -(parameters with all the extract info) (see [here](https://developer.wordpress.org/cli/commands/post/create/))

- [ ] Fetch images from file directory - _figure out permissions needed to connect to server_ (should be called name name inside the digital folder of the right week) (somehow - need to store them somewhere remote or maybe run from a newsroom computer but that would not be good)
- [ ] RESIZE IMAGES IF NECESSARY!
- [ ] Add downloaded images to uploaded article using [this command](https://developer.wordpress.org/cli/commands/media/import/)
### Dependencies (not complete)
- [ ] python, pandas, numpy, [pillow](https://github.com/python-pillow/Pillow) (obviously)
- [ ] wordpress, wp cli
- [ ] google drive API (currently using phillipiandev@gmail.com credentials)
- [ ] gspread
### To Upload Post
- Section specified via wp-post cli function argument
- Fill in:
  - _Author_ from article
  - _Title_ from headline
  - _Date_ from current time
- Content imported from google docs

- Use uploaded post id to add photos
### To Add Media
- We can either use the photo directory name or have photo host their images elsewhere online
- This command attaches an image for post 1:
  - `wp media import <file or url> --title='Something' --post_id=1`
  - Set the `--featured-image` flag to set the post thumbnail displayed on the homepage _(default to setting the flag on the first image)_

### Instructions for Setup
Download Wordpress and Wordpress CLI and begin making posts. This feels a bit hacky and not altogether right but I don't know how else to do it.
- Set up a localhost wordpress website by following [this](https://crunchify.com/how-to-install-wordpress-locally-on-mac-os-x-using-mamp/) tutorial
- Download wordpress CLI using the installing instructions [here](https://wp-cli.org/) -- you have to scroll down a lot
- You can now run wp commands but you have to be in /Applications/MAMP/htdocs/wordpress/wp-includes (or you could just pass it into the command with --path=/Applications/MAMP/htdocs/wordpress or just cd into that directory inside the script which is what is there right now)
- Troubleshoot if there are any issues
- You should be able to run _wp post create --from-post=1 --post_title='Testing wp cli'_ and see it when you run _wp post list_

### Troubleshooting:
- **If in** /Applications/MAMP/htdocs/wordpress/wp-includes
- **Running** wp admin
- **Yields** Error establishing a database connection. This either means that the username and password information in your `wp-config.php` file is incorrect or we can’t contact the database server at `localhost`. This could mean your host’s database server is down.
- **Then** find the wp-config.php file which should be in the main wordpress folder and change localhost in wp-config.php to 127.0.0.1:8889 or 127.0.0.1:3306 or 127.0.0.1:<whatever port you have on MAMP>
