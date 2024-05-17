import os
import sys
import argparse
# import requests
import xml.etree.ElementTree as ET

prog = 'Wordpress To Static'
description = 'Given a WRX, this program will create a static copy of it\'s website'
help = 'An exported WRX .xml file to use for copying'
# data_path = os.path.join(os.getcwd(), 'data')
# default_output_file = os.path.join(data_path, 'output.json')
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


def extract_wrx_page_links(wrx_path: str):
    tree = ET.parse(wrx_path)
    channel = tree.getroot()[0]
    title_key = 'title'
    link_key = 'link'
    status_key = '{http://wordpress.org/export/1.2/}status'
    base_page_title = channel.find(title_key).text
    base_page_link = channel.find(link_key).text
    items = []

    for item in channel.findall('item'):
        item_title = item.find(title_key).text
        item_link = item.find(link_key).text
        item_status = item.find(status_key).text
        items.append({
            title_key: item_title,
            'status': item_status,
            link_key: item_link
        })

    print(f'channel tag: {channel.tag}')
    print(f'base page title: {base_page_title}')
    print(f'base page link: {base_page_link}')
    print(f'items: {items}')


if __name__ == '__main__':
    wrx_file = parse_arg()
    extract_wrx_page_links(wrx_file)
