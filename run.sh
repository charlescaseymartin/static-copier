#!/usr/bin/bash

root_url=$1
domain=$(echo $root_url | sed -e 's/[^/]*\/\/\([^@]*@\)\?\([^:/]*\).*/\2/')
stored_directory=$2

wget \
-nH \
--mirror \
--convert-links \
--adjust-extension \
--page-requisites \
--no-parent \
--no-clobber \
--wait=0.5 \
--reject-regex=".*/(\?p=|wp-json|feed|xmlrpc).*" \
--domains=$domain \
--directory-prefix=$stored_directory \
$root_url

rm -rf "$stored_directory/wp-admin"
find $stored_directory -name "wp-login*" -delete
find $stored_directory -name "*.html" -exec sed -i 's|/index.html"|/"|g' {} +
