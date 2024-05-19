import os
import sys
import argparse
# import requests
import xml.etree.ElementTree as ET

prog = 'Wordpress To Static'
description = 'Given a WRX, this program will create a static copy of it\'s website'
help = 'An exported WRX .xml file to use for copying'
# data_path = os.path.join(os.getcwd(), 'data')
# user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/81.0'
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


def get_static_pages():
    pass


def main():
    wrx_file = parse_arg()
    pages = get_wrx_pages(wrx_file)
    print(f'pages: {pages}')


if __name__ == '__main__':
    main()
