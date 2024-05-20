import os
import sys
from pathlib import Path
import shutil
import argparse
import requests
import xml.etree.ElementTree as ET

prog = 'Wordpress To Static'
description = 'Given a WRX, this program will create a static copy of it\'s website'
help = 'An exported WRX .xml file to use for copying'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0'
parser = argparse.ArgumentParser(prog=prog, description=description)
parser.add_argument('-w', '--wrx', required=False, nargs=1, help=help)


def parse_arg():
    args = parser.parse_args()
    wrx_file = args.wrx[0] if args.wrx else ''

    if not os.path.isfile(wrx_file):
        print('[ERROR]: Invalid WRX file path\n')
        parser.print_help()
        sys.exit(1)

    return wrx_file


def get_wrx_pages(wrx_path: str):
    pages = []
    tree = ET.parse(wrx_path)
    channel = tree.getroot()[0]
    title_key = 'title'
    link_key = 'link'
    published_key = 'published'
    status_key = '{http://wordpress.org/export/1.2/}status'
    base_title = channel.find(title_key).text
    base_link = channel.find(link_key).text
    pages.append({
        title_key: base_title,
        published_key: True,
        link_key: base_link,
    })

    for page in channel.findall('item'):
        page_title = page.find(title_key).text
        page_link = page.find(link_key).text
        page_status = page.find(status_key).text
        is_published = True if page_status == 'publish' else False
        pages.append({
            title_key: page_title,
            published_key: is_published,
            link_key: page_link,
        })

    return pages


def create_website_structure():
    static_dir = os.path.join(os.getcwd(), 'static')
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)

    Path(f'{static_dir}/assets/css').mkdir(parents=True, exist_ok=True)
    Path(f'{static_dir}/assets/images').mkdir(parents=True, exist_ok=True)
    Path(f'{static_dir}/assets/fonts').mkdir(parents=True, exist_ok=True)
    Path(f'{static_dir}/assets/js').mkdir(parents=True, exist_ok=True)


def get_static_pages(pages: list):
    create_website_structure()
    for page in pages:
        if page['published']:
            headers = {'User-Agent': user_agent}
            res = requests.get(page['link'], headers=headers)
            if res.status_code == 200:
                print('write html content!')


def main():
    wrx_file = parse_arg()
    pages = get_wrx_pages(wrx_file)
    get_static_pages(pages)


if __name__ == '__main__':
    main()
