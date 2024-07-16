import os
import sys
from pathlib import Path
import shutil
import argparse
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import re

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


def fetch_data(url=''):
    if len(url) < 1:
        Exception('Fetch data needs a URL')
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    return response


def get_static_pages(pages: list):
    create_website_structure()
    for page in pages:
        if page['published']:
            res = fetch_data(page['url'])
            if res.status_code == 200:
                create_static_dirs(page['path'])
                html_file_path = f'{static_dir}{page['path']}/index.html'
                with open(html_file_path, 'w') as html_file:
                    parsed_html = BeautifulSoup(res.text, 'lxml').prettify()
                    html_file.write(parsed_html)


def fetch_css_files(css_links=[]):
    if len(css_links) < 1:
        Exception('Can not fetch css files, no links provided.')

    for link in css_links:
        filename = '.'.join(link.split('/')[-2:]).split('?')[0]
        css_save_path = f'{static_dir}/assets/css/{filename}'
        res = fetch_data(link)
        if res.status_code == 200:
            with open(css_save_path, 'w') as css_file:
                css_file.write(res.text)


def fetch_font_files(font_links=[]):
    if len(font_links) < 1:
        Exception('Can not fetch font files, no links provided.')

    for link in font_links:
        filename = ''.join(link.split('/')[-1])
        font_save_path = f'{static_dir}/assets/fonts/{filename}'
        res = fetch_data(link)
        if res.status_code == 200:
            with open(font_save_path, 'w') as font_file:
                font_file.write(res.text)


def fetch_js_files(js_links=[]):
    print(f'{js_links}')


def fetch_image_files(image_links=[]):
    print(f'{image_links}')


def get_static_page_assets():
    all_css_links = set()
    all_font_links = set()
    all_js_links = set()
    all_images_links = set()

    for path, subdir, files in os.walk(static_dir):
        if 'assets' not in path:
            with open(f'{path}/{files[0]}', 'r') as page:
                parsed_content = BeautifulSoup(page.read(), 'lxml')

                # get css file links
                css_attrs = {'rel': 'stylesheet'}
                css_links = parsed_content.find_all(attrs=css_attrs)
                all_css_links.update([link['href'] for link in css_links])

                # get font file links
                font_attrs = {'id': 'wp-fonts-local'}
                font_tag = parsed_content.find_all('style', attrs=font_attrs)[0]
                font_styles = re.findall(r'url\(.*\)\s', font_tag.string)
                for link in font_styles:
                    parsed_link = link.replace("url('", '').replace("') ", '')
                    all_font_links.add(parsed_link)

                # get js file links
                # get script tag src's
                script_src_tags = parsed_content.find_all('script', attrs={'src': True})
                [all_js_links.add(tag['src']) for tag in script_src_tags]
                # get link tag href's
                link_src_attrs = {'id': '@wordpress/interactivity-js-modulepreload'}
                link_js_tags = parsed_content.find_all('link', attrs=link_src_attrs)
                [all_js_links.add(tag['href']) for tag in link_js_tags]
                # check script content for imports

                # get image links

    fetch_css_files(list(all_css_links))
    fetch_font_files(list(all_font_links))
    fetch_js_files(list(all_js_links))
    # fetch_image_files(list(all_images_links))


def update_static_page_urls():
    # replace all urls with static versions:
    # - css linked files
    # - js linked files
    # - image links
    # - font imports
    # - navigations to other pages
    pass


if __name__ == '__main__':
    wrx_file = parse_arg()
    pages = get_wrx_pages(wrx_file)
    get_static_pages(pages)
    get_static_page_assets()
    update_static_page_urls()
