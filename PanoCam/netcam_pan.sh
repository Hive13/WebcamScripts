#!/bin/bash

# Script Options
WAIT_TIME=15

# Wget parameters
URL_TIMEOUT=30
URL_FAIL_IMG=fail.jpg

# Mobile Camera Variables
CAM_PAN_URL="http://172.16.3.252//-wvhttp-01-/GetStillImage?camera_id=1&v=640"
CAM_PAN_PARAMS="&b=ON&option=skip_on_error&seq="
IMG_ARC_1="&p=-80&t=-20&z=10"
IMG_ARC_2="&p=-35&t=-15&z=10"
IMG_ARC_3="&p=0&t=-15&z=10"
IMG_ARC_4="&p=40&t=-15&z=10"
IMG_ARC_5="&p=80&t=-15&z=10"

# Static Camera Variables
IMG_URL=http://172.16.3.243/fullsize.jpg
IMG_NAME=arc
IMG_URL_PARAMS=?clock=off

# Time Overlay options:
TIME_OVERLAY="time.png"
TIME_IMAGE_NAME="fullsize_clock.jpg"
TIME_FONTSIZE=12
TIME_FONT=/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono.ttf

# Archiving variables 
PREV_DATE=$(date +"%Y%m%d")

cd /home/hivecam/webcamArchiver 

# Script combined variables for easy coding reference
CAM_PAN_ARC_1="${CAM_PAN_URL}${IMG_ARC_1}${CAM_PAN_PARAMS}1"
CAM_PAN_ARC_2="${CAM_PAN_URL}${IMG_ARC_2}${CAM_PAN_PARAMS}2"
CAM_PAN_ARC_3="${CAM_PAN_URL}${IMG_ARC_3}${CAM_PAN_PARAMS}3"
CAM_PAN_ARC_4="${CAM_PAN_URL}${IMG_ARC_4}${CAM_PAN_PARAMS}4"
CAM_PAN_ARC_5="${CAM_PAN_URL}${IMG_ARC_5}${CAM_PAN_PARAMS}5"

echo "INFO: Getting pan position 1"
wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_1.jpg $CAM_PAN_ARC_1
WGET_ERROR=$?

echo "INFO: Getting pan position 2"
wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_2.jpg $CAM_PAN_ARC_2
WGET_ERROR=$?

echo "INFO: Getting pan position 3"
wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_3.jpg $CAM_PAN_ARC_3
WGET_ERROR=$?

echo "INFO: Getting pan position 4"
wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_4.jpg $CAM_PAN_ARC_4
WGET_ERROR=$?

echo "INFO: Getting pan position 5"
wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_5.jpg $CAM_PAN_ARC_5
WGET_ERROR=$?


# Upload image to the interwebs
echo "INFO: uploading image..."
scp ${IMG_NAME}_1.jpg webcam1@shell.hive13.org:/var/www/webcam1/${IMG_NAME}_1.jpg
scp ${IMG_NAME}_2.jpg webcam1@shell.hive13.org:/var/www/webcam1/${IMG_NAME}_2.jpg
scp ${IMG_NAME}_3.jpg webcam1@shell.hive13.org:/var/www/webcam1/${IMG_NAME}_3.jpg
scp ${IMG_NAME}_4.jpg webcam1@shell.hive13.org:/var/www/webcam1/${IMG_NAME}_4.jpg
scp ${IMG_NAME}_5.jpg webcam1@shell.hive13.org:/var/www/webcam1/${IMG_NAME}_5.jpg

