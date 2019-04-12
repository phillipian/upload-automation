# Phillipian Article Upload Automation
Project to automate uploading to phillipian.net
### Structure
upload_script.py is the main script. It will be run from a docker container on a computer in the newsroom to more easily access the photo server.
### Usage
- Article text will appear as it does in the Google Doc
- Things have to be standardized, like folder names on the path to image dirs, and all photos should be in the digital directory
- Can we put pulled photos on the budget too
- Fill out the budget
  - Use these fields: 'Headline' (for sports, make sure the team name is somewhere in there)
  - New fields: 'Link' (explicit link to Google doc), 'Upload?' ('yes'/'no'; whether article is ready for upload), 'Featured?' (whether article is featured), and 'ImageDir' (image directory within the digital folder)
  - Photo: 'Caption', 'Photographer' (for credit), 'ImageDir' (should match ImageDir from writing section)
- Add BOF and EOF markers in article doc (‘BOFCXLII’, ‘EOFCXLII’) (the doc must be the final version of the article)
- Run the script: python upload_script.py --url URL
- Check and publsih all posts (the script will make them drafts)
- Upload editorial and multilingual manually

- Docker: docker cp /Volumes/Phillipian/Phillipian/Spring-2019/4-12/digital/ container:/imgs
  - docker exec -it container /bin/bash
  - To check status, use Kitematic (if you are Alex) and use docker ps -a (if you are not)
### Jobs
- [ ] Jeffrey - create/assign authors for all past articles (preserving compatability for current mechanisms), add multiple author functionality, create compatability with the old phillipian.net with custom field plug-in for authors.
- [ ] Alex - make a docker image with everything needed for easier running, try uploading on the **real** website (configging etc)
- [ ] Sarah - end to end testing, generate complete budget, output message for spreads saying to upload photos manually, output message for missing EOF and BOF strings / if not formatted right, add quotes around cd, ask to standardize format for photographer
### To Do
- [ ] Change config file to access real website
### Project Workflow
- [ ] Fetch **budget data** using drive CLI 
- [ ] Extract **article text** from slug column using drive CLI
- [ ] Post to the website us wp post create -(parameters with all the extract info) (see [here](https://developer.wordpress.org/cli/commands/post/create/))
- [ ] Fetch and resize images from file directory - _figure out permissions needed to connect to server_ (should be called name name inside the digital folder of the right week) (somehow - need to store them somewhere remote or maybe run from a newsroom computer but that would not be good)
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
