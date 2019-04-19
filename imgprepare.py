import os
from PIL import Image

def img_for_post_content(url: str, caption: str = "", credit: str = ""):
    """Returns the string used to insert an image, caption, and credit into the post content"""
    img_markdown = f"<img src=\"{url.strip()}\" />"

    if credit.strip():
        img_markdown = f"[media-credit name=\"{credit}\"]{img_markdown}[/media-credit]"

    if caption.strip():
        img_markdown = f"[caption]{img_markdown} {caption}[/caption]"

    return img_markdown


def compress_img(fp: str, jpeg_quality: int = 90):
    """Compresses the image at the specified file path.
    
    Args:
        fp: the file path
        jpeg_quality: the quality of the compressed image (1-95)
    Returns:
        the path of the compressed image
    """
    img = Image.open(fp).copy()

    maxsize = (1280, 1280)
    img.thumbnail(maxsize, Image.ANTIALIAS)
    new_fp = os.path.dirname(fp) + '/Compressed_' + os.path.basename(fp)

    img.save(new_fp, "JPEG", quality=jpeg_quality, optimize=True)
    return new_fp