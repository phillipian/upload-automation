# Phillipian Article Upload Automation
Project to automate uploading to phillipian.net
### Jobs
- [ ] Jeffrey - figure out how to make a docker image with everything needed for easier running
- [ ] Alex - **figure out how to display image**; style template image to display caption and credit
- [ ] Sarah - figure out how to upload on the real website; get things standardized on budget!
### Logistical To Do
- [ ] Figure out how to access the photo server (we might just run it on a newsroom computer)
- [ ] Standardizes slug and headline columns
- [ ] Get a url column, photo directory column in budget
- [ ] Get a standardized end of article string in each Google Document
- [ ] Have to change config file to access real website
- [ ] Can we get phillipian.com?
### Project Requirements
- [ ] Probably **download budget** from the folder using drive CLI 
- [ ] Extract **article text** from slug column (get from start to page break) also probably using drive CLI
- [ ] Extract **writer, headline, and section** from budget
- [ ] Post to the website us wp post create -(parameters with all the extract info) (see [here](https://developer.wordpress.org/cli/commands/post/create/))

- [ ] Extract **photo directory name** (it will be a new column in the budget)
- [ ] Fetch images from file directory - _figure out permissions needed to connect to server_ (should be called name name inside the digital folder of the right week) (somehow - need to store them somewhere remote or maybe run from a newsroom computer but that would not be good)
- [ ] RESIZE IMAGES IF NECESSARY!
- [ ] Add downloaded images to uploaded article using [this command](https://developer.wordpress.org/cli/commands/media/import/)
### Dependencies (not complete)
- [ ] python, pandas, numpy (obviously)
- [ ] wordpress, wp cli
- [ ] google drive API (currently using phillipiandev@gmail.com credentials)
- [ ] gspread
### To Upload Post
- Section specified via wp-post cli function argument
- Fill in:
  - Author from article
  - Title from headline
  - Date from current time
- Content imported from google docs

- Use uploaded post id to add photos
### To Add Media
- We can either use the photo directory name or have photo host their images elsewhere online
- This command attaches an image for post 1:
  - wp media import <file or url> --title='Something' --post_id=1
- The theme file template-parts/content-single.php must be edited to display attachments, and it must be styled to display captions and credits
  - On the CityNews theme, the code for single posts may lie in `tpl/tpl-loop.php`. We can easily override this file in the child theme.

### Instructions for Setup
Download Wordpress and Wordpress CLI and begin making posts. This feels a bit hacky and not altogether right but I don't know how else to do it.
- Set up a localhost wordpress website by following [this](https://crunchify.com/how-to-install-wordpress-locally-on-mac-os-x-using-mamp/) tutorial
- Download wordpress CLI using the installing instructions [here](https://wp-cli.org/) -- you have to scroll down a lot
- You can now run wp commands but you have to be in /Applications/MAMP/htdocs/wordpress/wp-includes (or you could just pass it into the command with --path=/Applications/MAMP/htdocs/wordpress or just cd into that directory inside the script which is what is there right now)
- Troubleshoot if there are any issues
- You should be able to run *wp post create --from-post=1 --post_title='Testing wp cli'* and see it when you run *wp post list*

### Troubleshooting:
- **If in** /Applications/MAMP/htdocs/wordpress/wp-includes
- **Running** wp admin
- **Yields** Error establishing a database connection. This either means that the username and password information in your `wp-config.php` file is incorrect or we can’t contact the database server at `localhost`. This could mean your host’s database server is down.
- **Then** find the wp-config.php file which should be in the main wordpress folder and change localhost in wp-config.php to 127.0.0.1:8889 or 127.0.0.1:3306 or 127.0.0.1:<whatever port you have on MAMP>
