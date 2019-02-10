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
