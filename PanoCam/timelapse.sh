#!/bin/bash

# Mencoder options
FPS=24          # 24 FPS = (24 hours * 60 minutes * 2 shots a minute) / 120 (2 minutes of time lapse film)
BITRATE=2160000

ARCHIVE_DIR=/home/pvince/webcamFiles

IN_FILE=$1
IN_DATE=""

if [ "$2" == "" ]
then
  IN_DATE=`echo $1 | cut -d'_' -f2 | cut -d'.' -f1`
  echo "INFO: IN_DATE parsed from $1 to $IN_DATE"
else
  IN_DATE=$2
  echo "INFO: IN_DATE set via parameter to $IN_DATE"
fi

if [ "$IN_FILE" == "" -o "$IN_DATE" == "" ]
then
  echo Incorrect usage.  Expected two parameters, ex. timelapse.sh ImageArchive.tar.gz 20110824
  exit 1
fi

if [ ! -f $IN_FILE ]
then
  echo "$IN_FILE does not exist."
  exit 1
fi

# Extract the "In File" to individual images.
echo "INFO: Extracting $IN_FILE..."
mkdir $IN_DATE
tar -C $IN_DATE -zxf $IN_FILE

# Encode the final time lapse
echo "INFO: Encoding timelapse video..."
mencoder -nosound mf://$IN_DATE/*.jpg -mf w=352:h=288:type=jpg:fps=$FPS -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=$BITRATE:mbd=2:keyint=132:v4mv:vqmin=3:lumi_mask=0.07:dark_mask=0.2:mpeg_quant:scplx_mask=0.1:tcplx_mask=0.1:naq -o webvid_$IN_DATE.avi

# Clean up extracted images.
echo "INFO: Cleaning up extracted images..."
rm -rf $IN_DATE

# Upload the finished timelapse to youtube
# echo "INFO: Uploading timelapse video to YouTube..."
# google youtube post -u pvince@gmail.com -t "Hive13, hackerspace, timelapse, webcam" --src=webvid_$IN_DATE.avi -c Tech 

# Archive the image archive and webcam footage
echo "INFO: Archiving image archive and timelapse video"
mv $IN_FILE $ARCHIVE_DIR
mv webvid_$IN_DATE.avi $ARCHIVE_DIR
