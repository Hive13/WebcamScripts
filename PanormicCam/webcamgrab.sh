#!/bin/bash

# Script Options
WAIT_TIME=15

# Wget parameters
URL_TIMEOUT=30
URL_FAIL_IMG=fail.jpg
IMG_URL=http://172.16.3.243/fullsize.jpg
IMG_NAME=fullsize.jpg
IMG_URL_PARAMS=?clock=off

# Time Overlay options:
TIME_OVERLAY="time.png"
TIME_IMAGE_NAME="fullsize_clock.jpg"
TIME_FONTSIZE=12
TIME_FONT=/usr/share/fonts/truetype/ttf-dejavu/DejaVuSansMono.ttf

# Archiving variables 
PREV_DATE=$(date +"%Y%m%d")

cd /home/pvince/webcamArchiver 

while [ 1 ]
do
  echo "INFO: Getting ethernet webcam image..."
  wget --read-timeout=$URL_TIMEOUT -O $IMG_NAME ${IMG_URL}${IMG_URL_PARAMS}
  WGET_ERROR=$?

  if [ $WGET_ERROR == "0" ]
  then
    echo "INFO: got image successfully!"
    INFILE=$IMG_NAME
  else
    echo "INFO: failed to get webcam image! Error code = $WGET_ERROR"
    INFILE=$URL_FAIL_IMG
  fi

  echo "INFO: adding clock overlay..."
  TIMESTR=$(date +"%Y.%m.%d %H:%M:%S")
  # Generate clock overlay with $TIMESTR text.
  convert -font $TIME_FONT -pointsize $TIME_FONTSIZE label:"$TIMESTR" $TIME_OVERLAY
  # Add overlay to image.
  convert $INFILE $TIME_OVERLAY -gravity NorthEast -compose over -composite $TIME_IMAGE_NAME

  # Upload image to the interwebs
  echo "INFO: uploading image..."
  scp $TIME_IMAGE_NAME webcam1@shell.hive13.org:/var/www/webcam1/fullsize.jpg

  # Push image to daily tar archive.
  echo "INFO: adding image to archive..."
  IMG_ARC_NAME=$(date +"webimg_%Y%m%d_%H%M%S.jpg")
  ARC_NAME=$(date +"webimgs_%Y%m%d.tar")
  mv $TIME_IMAGE_NAME $IMG_ARC_NAME
  tar -rf $ARC_NAME $IMG_ARC_NAME
  rm $IMG_ARC_NAME
  
  # Check the date, new date? Zip up the archive, delete the tar, copy to storage directory.
  CUR_DATE=$(date +"%Y%m%d")
  if [ $PREV_DATE != $CUR_DATE ]
  then
    echo "INFO: new date detected! Zipping up the image archive. Please stand by..."
    gzip -9 webimgs_${PREV_DATE}.tar
    echo "INFO: Image archived zipped. Kicking off timelapse generation."
    ./timelapse.sh webimgs_${PREV_DATE}.tar.gz >> timelapse.log 2>&1 &
    PREV_DATE=$CUR_DATE
  fi

  echo "INFO: Finished... Next run in $WAIT_TIME seconds"
  echo "------------------------------------------------"
  sleep $WAIT_TIME
done
