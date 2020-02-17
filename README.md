# Phillipian Article Upload Automation
Project to automate uploading to phillipian.net

### Docker for development
In `./docker`, run the following commands to access bash in a docker image with all Python dependencies in `requirements.txt` installed and with this repo mounted at `usr/src/app` :
```
docker build -t plip-env . 
docker run -it -v [PATH TO THIS GIT REPO]:/usr/src/app plip-env /bin/bash
```
We should Dockerize soon (so that just running the docker image will run upload) ([a simple guide](https://runnable.com/docker/python/dockerize-your-python-application)).

### Running
Run local_preprocess.py from a local machine with access to the week's photos to compress images, fetch filtered articles, and prepend image info/author name to the beginning of each article. Those files will be scp-ed to the server. Then run remote_upload.py to read the info from the article text files and call the necessary wordpress commands to actually upload.
### Usage
- We are currently working on expanding support for uploading spreads, editorial, eighth page, and multilingual
- Article Google Docs
  - Article text will appear as it does in the doc, so please place the final article back on the doc if changes are made
  - Add BOF and EOF markers in article doc (‘BOFCXLII’, ‘EOFCXLII’) (the doc must be the final version of the article)
- All photos/illustrations should be in the digital directory. Also, folder names on the path have to be standardized, sorry!
- Filling out the budget
  - Use these fields: 'Headline' (for sports, make sure the team name is somewhere in there)
  - New fields: 'Link' (explicit link to Google doc), 'Upload?' ('yes'/'no'; whether article is ready for upload), 'Featured?' (whether article is featured), and 'ImageDir' (image directory within the digital folder)
  - Photo: 'Caption', 'Photographer' (for credit), 'ImageDir' (should match ImageDir from writing section)
  - All photos/illustrations should also be on the budget (including ones that are pulled), with their photographer information so they can be properly fetched, captioned, and credited
- Check and publish all posts (the script will make them drafts)


- Docker: 
  - docker create -it --name container upload_container
  - docker cp /Volumes/Phillipian/Phillipian/Spring-2019/4-12/digital/ container:/imgs
  - docker start container
  - docker exec -it container /bin/bash
  - To check status, use Kitematic (if you are Alex) and use docker ps -a (if you are not)
### Project Workflow
- [ ] Fetch **budget data** using drive CLI 
- [ ] Extract **article text** from slug column using drive CLI
- [ ] Post to the website us wp post create -(parameters) (see [here](https://developer.wordpress.org/cli/commands/post/create/))
- [ ] Fetch and resize images from file directory
- [ ] Add downloaded images to uploaded article using [this command](https://developer.wordpress.org/cli/commands/media/import/)
### Dependencies (not complete)
- [ ] python, pandas, numpy, [pillow](https://github.com/python-pillow/Pillow) (obviously)
- [ ] wordpress, wp cli
- [ ] google drive API (currently using phillipiandev@gmail.com credentials)
- [ ] gspread
- [ ] [pytesseract](https://pypi.org/project/pytesseract/)
- [ ] [unidecode](https://pypi.org/project/Unidecode/)
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
