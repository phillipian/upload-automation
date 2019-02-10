# upload-automation
Project to automate uploading to phillipian.net

### Project Requirements
- [ ] Probably download budget from the folder using drive CLI 
- [ ] Extract article from slug column (get from start to page break) also probably using drive CLI
- [ ] Extract writer and headline and section
- [ ] Post to the website us wp post create -(parameters with all the extract info)
- [ ] Extract photo directory name (it will be a new column in the budget)
- [ ] Fetch images from file directory (should be called name name inside the digital folder of the right week) (somehow - need to store them somewhere remote or maybe run from a newsroom computer but that would not be good)
- [ ] Post to the corresponding article using wp media

### To Upload Post
- Section specified via wp-post cli function argument
- Fill in:
  - Author from article
  - Title from headline
  - Date from current time
- Content imported from google docs
