#!/usr/bin/env bash
#
# Download ALOS DEM data
#
# Register for access at https://www.eorc.jaxa.jp/ALOS/en/aw3d30/index.htm
#
# Usage:
#   bash get_jaxa_alos_dem_data.sh <username> <password>
#

# quit at first error
set -e

user=$1
password=$2

echo "Downloading ALOS DEM for user '$user' with ${#password}-character password"

# get index page
wget --user $user --password $password https://www.eorc.jaxa.jp/ALOS/en/aw3d30/data/index.htm

# extract tile pages
grep -oP "html_v1903[^\"]*" index.htm \
    | awk '{printf("https://www.eorc.jaxa.jp/ALOS/en/aw3d30/data/%s\n", $1)}' \
    > tiles.txt

# get tile pages
wget --user $user --password $password -i tiles.txt

# extract list of data files
grep -ohP "comp\(.*\',\d" *.htm \
    | sed 's/comp(//' \
    | sed "s/'//g" \
    | cut -f 1,2 -d , \
    | awk -F, '{printf("https://www.eorc.jaxa.jp/ALOS/aw3d30/data/release_v1903/%s_%s.tar.gz\n", $1, $2)}' \
    > data.txt

# delete tile pages
rm *.htm

# get data

# get files one by one
#wget --user $user --password $password -i data.txt --continue

# open multiple requests in parallel (requires GNU parallel)
cat data.txt | parallel wget --user $user --password $password --continue

echo "Done."
