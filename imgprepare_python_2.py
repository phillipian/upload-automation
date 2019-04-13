import os
from PIL import Image
# python 2 version (I don't have python 3)
def img_for_post_content(url, caption, credit):
    """Returns the string used to insert an image, caption, and credit into the post content"""
    img_markdown = "<img src="+url.strip()+" />"

    if credit.strip():
        img_markdown = "[media-credit name="+credit+"]"+img_markdown+"[/media-credit]"

    if caption.strip():
        img_markdown = "[caption]"+img_markdown+" "+caption+"[/caption]"

    return img_markdown


def compress_img(fp, jpeg_quality):
    """Compresses the image at the specified file path.
    
    Args:
        fp: the file path
        jpeg_quality: the quality of the compressed image (1-95)
    Returns:
        the path of the compressed image
    """
    if (jpeg_quality == None):
        jpeg_quality = 90
    img = Image.open(str(fp)).copy()

    maxsize = (1280, 1280)
    img.thumbnail(maxsize, Image.ANTIALIAS)
    new_fp = os.path.dirname(fp) + '/0----Compressed_' + os.path.basename(fp)

    img.save(new_fp, "JPEG", quality=jpeg_quality, optimize=True)
    return new_fp
