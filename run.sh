#!/usr/bin/bash

help_menu () {
    hori_line='#################################'
    vert_line='#####'
    name='Website Static Copier'
    title="$hori_line\n$vert_line $name $vert_line\n$hori_line"
    usage='Usage:\tbash ./run.sh [URL] [DIR]\n\t-- OR --\n\tbash ./run.sh -h'
    arg_help='\t-h, --help\t Displays this menu.'
    arg_url='\t[URL]\t\t (REQUIRED) The website url from which to statically copy.'
    arg_dir='\t[DIR]\t\t (REQUIRED) The directory path to save the static website into.'
    printf "\n$title\n\n\n$usage\n\n\n$arg_help\n\n$arg_url\n\n$arg_dir"
    exit 1
}

if [[ $1 == '-h' ]] || [[ $1 == '--help' ]]; then help_menu; fi

root_url=$1
stored_directory=$2
valid_url_regex='(https?|ftp|file)://[-[:alnum:]\+&@#/%?=~_|!:,.;]*[-[:alnum:]\+&@#/%=~_|]'

[[ ! $root_url =~ $valid_url_regex ]] && help_menu;
[ -z $stored_directory ] && help_menu;
[ ! -d $stored_directory ] && mkdir -p $stored_directory

domain=$(echo $root_url | sed -e 's/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/')

wget \
-nH \
--mirror \
--convert-links \
--adjust-extension \
--page-requisites \
--no-parent \
--no-clobber \
--wait=0.5 \
--reject-regex='.*/(\?p=|wp-json|feed|xmlrpc).*' \
--domains=$domain \
--directory-prefix=$stored_directory \
$root_url

rm -rf '$stored_directory/wp-admin'
find $stored_directory -name 'wp-login*' -delete
find $stored_directory -name '*.html' -exec sed -i 's|/index.html"|/"|g' {} +
