# Phillipian Article Upload Automation
Project to automate uploading to phillipian.net

### Project Requirements
- [ ] Probably **download budget** from the folder using drive CLI 
- [ ] Extract **article text** from slug column (get from start to page break) also probably using drive CLI
- [ ] Extract **writer, headline, and section** from budget
- [ ] Post to the website us wp post create -(parameters with all the extract info) (see [here](https://developer.wordpress.org/cli/commands/post/create/))

- [ ] Extract **photo directory name** (it will be a new column in the budget)
- [ ] Fetch images from file directory - _figure out permissions needed to connect to server_ (should be called name name inside the digital folder of the right week) (somehow - need to store them somewhere remote or maybe run from a newsroom computer but that would not be good)
- [ ] Add downloaded images to uploaded article using [this command](https://developer.wordpress.org/cli/commands/media/import/)

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
- This command sets a featured image for post 1:
  - wp media import <file or url> --title='Something' --post_id=1 --featured_image
- Figure out how to upload more than just the featured image using wp media import
- The theme file template-parts/content-single.php must be edited to display attachments, or its equivalent

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
