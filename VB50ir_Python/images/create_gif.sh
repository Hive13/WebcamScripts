#!/bin/sh

source="/home/username/canon_webview/images/"
dest="/home/username/canon_webview/images/"
today=`date +"%Y%m%d"`

convert -layers optimize -delay 40 ${source}*_${today}*.jpg ${dest}animation_${today}.gif
