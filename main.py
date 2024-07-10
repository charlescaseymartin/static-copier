import os
import sys
from pathlib import Path
import shutil
import argparse
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

prog = 'Wordpress To Static Site'
description = 'Given a WRX, this program will create a static copy of it\'s website'
help = 'An exported WRX .xml file to use for copying'
user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0'
parser = argparse.ArgumentParser(prog=prog, description=description)
parser.add_argument('-w', '--wrx', required=False, nargs=1, help=help)
static_dir = os.path.join(os.getcwd(), 'static')


def parse_arg():
    args = parser.parse_args()
    wrx_file = args.wrx[0] if args.wrx else ''

    if not os.path.isfile(wrx_file):
        print('[ERROR]: Invalid WRX file path\n')
        parser.print_help()
        sys.exit(1)

    return wrx_file


def get_page_url_path(url):
    path = '/'.join(str(url).split('/')[3:])
    return f'/{path}'


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
        'url': base_link,
        'path': get_page_url_path(base_link),
    })

    for page in channel.findall('item'):
        page_title = page.find(title_key).text
        page_link = page.find(link_key).text
        page_status = page.find(status_key).text
        is_published = True if page_status == 'publish' else False
        pages.append({
            title_key: page_title,
            published_key: is_published,
            'url': page_link,
            'path': get_page_url_path(page_link),
        })

    return pages


def create_static_dirs(dir: str):
    Path(f'{static_dir}{dir}').mkdir(parents=True, exist_ok=True)


def create_website_structure():
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)

    create_static_dirs('/assets/css')
    create_static_dirs('/assets/images')
    create_static_dirs('/assets/fonts')
    create_static_dirs('/assets/js')


def get_static_pages(pages: list):
    create_website_structure()
    for page in pages:
        if page['published']:
            headers = {'User-Agent': user_agent}
            res = requests.get(page['url'], headers=headers)
            if res.status_code == 200:
                create_static_dirs(page['path'])
                html_file_path = f'{static_dir}{page['path']}/index.html'
                with open(html_file_path, 'w') as html_file:
                    parsed_html = BeautifulSoup(res.text, 'lxml').prettify()
                    html_file.write(parsed_html)


def get_static_page_assets():
    for path, subdir, files in os.walk(static_dir):
        if 'assets' not in path:
            print(f'path: {path}\nsub directory: {subdir}\nfiles: {files}')
            # get css files
            # get font files
            # get js files
            # get images


if __name__ == '__main__':
    wrx_file = parse_arg()
    pages = get_wrx_pages(wrx_file)
    get_static_pages(pages)
    get_static_page_assets()
