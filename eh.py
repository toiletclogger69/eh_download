#! python3
"""
###############################################################
made by toiletclogger69
https://github.com/toiletclogger69/eh_download

pip install gooey requests bs4

to run :
python eh.py (launch the gooey app)

if you don't want to use gooey and only this script, you can call download_gallery directly, eg :
download_gallery(url_to_the_gallery_you_want, true)

you can set TRUE_IF_CLI = True if you want to use the script directly with a text file "urls.txt" containing all urls

###############################################################

download a list of gallery from e-hentai
you can pass a list of url in the text area and it will download every page,
and put them in their respective gallery folder

###############################################################
3~4s between the download of each page, or you get flagged as a bot

the images downloaded are the sample resolution for eh (1280 * xxxx), if you want better resolution go with a torrent
"""

from sys import stdout, exit
from os import path, makedirs, getcwd
from time import sleep
from random import randint

import requests
from bs4 import BeautifulSoup
from gooey import Gooey, GooeyParser


# python -m venv env && env\Scripts\activate.bat


# change this var to change the folder name
GALLERY_FOLDER = "doujins"

''' add a urls.txt file in the current folder, add every urls inside, separated by a newline eg:
https://e-hentai.org/g/lots_of_number1/lots_of_number1/
https://e-hentai.org/g/lots_of_number2/lots_of_number2/
https://e-hentai.org/g/lots_of_number3/lots_of_number3/
then set this to True and execture the script with python eh.py'''
TRUE_IF_CLI = False
# TRUE_IF_CLI = True


headers = {"User-Agent" : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}


###############################################################


def download_gallery(url='', true_if_replace_name=False) -> int:
    # ignore warning "offensive content"
    if "?nw=always" not in url:
        url += "?nw=always"

    html_request = requests.get(url, headers=headers)
    html_request.raise_for_status()
    html_page = BeautifulSoup(html_request.text, 'html.parser')

    # if wrong url, or error 404
    if "Key missing, or incorrect key provided." in html_page.text or "error 404" in html_page.text:
        print(f"couldn't find {url}")
        print("-1%")
        stdout.flush()
        sleep(6)
        return

    # find title
    title_bs4 = html_page.find('title')
    title_gallery = title_bs4.text.split(" - E-Hentai Galleries")[0]

    # find number of pages
    meta = html_page.find_all(class_ ="gdt2")
    number_of_page = [x for x in meta if "pages" in x.text][0].text
    number_of_page = int(number_of_page.split(" pages")[0])

    # find first page url
    first_page = html_page.find_all(class_ ="gdtm")[0]
    url_next_page = first_page.find('a')['href']

    # create the folder
    if true_if_replace_name:
        title_gallery = ''.join(char for char in title_gallery if (char.isalnum() or char in r"_-[]()\{\} "))
    gallery_path = path.join(getcwd(), GALLERY_FOLDER, title_gallery)
    makedirs(gallery_path, exist_ok=True)

    # informations
    print("\n\n============================\n")
    print(f'\t{number_of_page} pages - {url}')
    
    # issue with UnicodeEncodeError when using Gooey, issue seems difficult to fix properly so instead we just ignore it
    try:
        print(f'\t{title_gallery}')
    except UnicodeEncodeError:
        print("\tThis windows cannot display non-ascii character, cannot display the title")
    print("\n----------------------------\n")

    for page_number in range(number_of_page):
        # don't touch the sleep amount or you will get flagged as a bot
        sleep(randint(3, 4))

        html_request = requests.get(url_next_page, headers=headers)
        html_request.raise_for_status()
        html_page = BeautifulSoup(html_request.text, 'html.parser')

        # find the picture div
        element_image = html_page.find("div", {"id": "i3"})

        # find the next url page link
        element_link = element_image.find('a')
        url_next_page = element_link['href']
        
        # find the current picture url
        element_source = element_image.find('img')
        url_image = element_source['src']

        # 0001.jpg, 0049.png, etc.
        file_name = path.basename(f"{str(page_number):0>4}.{url_image.split('.')[-1]}")

        content_image = requests.get(url_image, headers=headers)
        with open(path.join(gallery_path, file_name), 'wb+') as file:
            for chunk in content_image.iter_content(100000):
                file.write(chunk)
        print(f"{file_name}\t\t{int((page_number / (int(number_of_page) - 1)) * 100):0>2}%")

        stdout.flush()
    return 1


@Gooey(progress_regex=r"(-?\d+)%$"
    , disable_progress_bar_animation=True
    , program_name='dgeh'
    , requires_shell=False
    , default_size=(500, 770)
    , program_description="Download gallery on eh"
    , menu=[{'name': 'About'
        , 'items': [{
            'type': 'AboutDialog'
            , 'menuTitle': 'About'
            , 'version': '1.1.3'
            , 'copyright': '2021'
            , 'website': 'https://github.com/toiletclogger69/eh_download'
            , 'developer': 'toiletclogger69'
        }]
    }]
)
def main():
    parser = GooeyParser(prog="gallery eh downloader")
    parser.add_argument('urls'
            , metavar='liste of url'
            , help='urls are separated by a newline, no blank line allowed'
            , widget='Textarea'
            , gooey_options={'height': 300, })
    parser.add_argument('-true_if_window_compatible'
        , metavar='Replace character'
        , action='store_true'
        , required=False
        , help='Some character ( / | ? ! etc. ) in gallery title are not valid in windows file name, if set those character will be removed')
    args = parser.parse_args()
    liste_urls = args.urls.split('\n')

    for current_url in liste_urls:
        if current_url and current_url.startswith("http"):
            download_gallery(current_url, args.true_if_window_compatible)
            print("")
            print("")
            print("-1%")
            stdout.flush()
            sleep(2)


if __name__ == "__main__":
    try:
        if TRUE_IF_CLI:
            """ Read every url from a text file """
            with open("urls.txt", 'r') as file_text:
                list_url = file_text.readlines()
            for current_url in list_url:
                if current_url and current_url.startswith("http"):
                    download_gallery(current_url, True)
        else:
            exit(main())
    except KeyboardInterrupt:
        print("\nEnd program")
