import os
import subprocess
from ebooklib import epub
from PIL import Image

PDF = "book.pdf"
IMG_DIR = "pages"
OUTPUT = "book_fixed.epub"

os.makedirs(IMG_DIR, exist_ok=True)

print("Converting PDF pages to PNG...")

subprocess.run([
    "pdftoppm",
    "-png",
    "-r",
    "200",
    PDF,
    os.path.join(IMG_DIR, "page")
], check=True)

images = sorted(
    f for f in os.listdir(IMG_DIR)
    if f.endswith(".png")
)

book = epub.EpubBook()

book.set_identifier("book")
book.set_title("Converted PDF")
book.set_language("en")

book.spine = ['nav']
book.toc = []

nav = epub.EpubNav()
book.add_item(nav)

css = epub.EpubItem(
    uid="style",
    file_name="style.css",
    media_type="text/css",
    content="""
html,body{
margin:0;
padding:0;
}
img{
width:100%;
height:100%;
display:block;
}
"""
)

book.add_item(css)

chapters = []

for i, img in enumerate(images):

    img_path = os.path.join(IMG_DIR, img)

    with Image.open(img_path) as im:
        w, h = im.size

    with open(img_path, "rb") as f:
        img_item = epub.EpubImage()

        img_item.file_name = f"images/{img}"
        img_item.media_type = "image/png"
        img_item.content = f.read()

    book.add_item(img_item)

    html = epub.EpubHtml(
        title=f"Page {i+1}",
        file_name=f"page{i+1}.xhtml"
    )

    html.content = f"""
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width={w}, height={h}"/>
        <link rel="stylesheet" href="style.css"/>
      </head>
      <body>
        <img src="{img_item.file_name}" />
      </body>
    </html>
    """

    book.add_item(html)

    chapters.append(html)

book.spine += chapters

epub.write_epub(OUTPUT, book)

print("Done!")
print("Created:", OUTPUT)