#!/bin/bash

# Script Options
WAIT_TIME=15

# Wget parameters
URL_TIMEOUT=30
URL_FAIL_IMG=fail.jpg

# Mobile Camera Variables
CAM_PAN_URL="http://172.16.3.252//-wvhttp-01-/GetStillImage?camera_id=1&v=640"
CAM_PAN_PARAMS="&b=ON&option=skip_on_error&seq="
IMG_MEETING="&p=-30&t=-30&z=1"
IMG_KITCHEN="&p=15&t=-25&z=1"
IMG_ELECTRONIC="&p=-47&t=-17"

# Static Camera Variables
IMG_URL=http://172.16.3.243/fullsize.jpg
IMG_NAME=fullsize
IMG_URL_PARAMS=?clock=off

# Time Overlay options:
TIME_OVERLAY="time.png"
TIME_IMAGE_NAME="fullsize_clock.jpg"
TIME_FONTSIZE=12
TIME_FONT=/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono.ttf

# Archiving variables 
PREV_DATE=$(date +"%Y%m%d")

cd /home/pvince/webcamArchiver 

# Script combined variables for easy coding reference
CAM_PAN_MEETING="${CAM_PAN_URL}${IMG_MEETING}${CAM_PAN_PARAMS}1"
CAM_PAN_KITCHEN="${CAM_PAN_URL}${IMG_KITCHEN}${CAM_PAN_PARAMS}2"
CAM_PAN_ELECTONIC="${CAM_PAN_URL}${IMG_ELECTRONIC}${CAM_PAN_PARAMS}3"

while [ 1 ]
do
  echo "INFO: Getting meeting webcam image..."
  wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_1.jpg $CAM_PAN_MEETING 
  WGET_ERROR=$?

  echo "INFO: Getting kitchen webcam image..."
  wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_2.jpg $CAM_PAN_KITCHEN
  WGET_ERROR=$?

  echo "INFO: Getting electronics bench webcam image..."
  wget --read-timeout=$URL_TIMEOUT -O ${IMG_NAME}_3.jpg $CAM_PAN_ELECTONIC

  WGET_ERROR=$?

  # Upload image to the interwebs
  echo "INFO: uploading image..."
  scp ${IMG_NAME}_1.jpg webcam1@shell.hive13.org:/var/www/webcam1/fullsize_1.jpg
  scp ${IMG_NAME}_2.jpg webcam1@shell.hive13.org:/var/www/webcam1/fullsize_2.jpg
  scp ${IMG_NAME}_3.jpg webcam1@shell.hive13.org:/var/www/webcam1/fullsize_3.jpg

  echo "INFO: Finished... Next run in $WAIT_TIME seconds"
  echo "------------------------------------------------"
  sleep $WAIT_TIME
done
