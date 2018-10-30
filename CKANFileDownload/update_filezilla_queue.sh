#!/usr/bin/env bash


function get_user_dir()
{
    IN_PATH_DEFAULT=$HOME
    read -p "Please enter folder path to save files to [$IN_PATH_DEFAULT]: " IN_PATH
    REPLACE_WITH="${IN_PATH:-$IN_PATH_DEFAULT}"

    if [ ! -d ${REPLACE_WITH} ]; then
        echo -e "Given folder location does not exist, please either create it or choose another location.\n"
        get_user_dir
    fi
}

START_FILE="/home/ianh/PycharmProjects/ckanpackager_service/ckanpackager/ckanpackager/utils/include_in_zipfile/FileZilla_Download_Queue.xml"

INPUT_FILE="/home/ianh/PycharmProjects/lorenzo/CKANFileDownload/FileZilla_Download_Queue-copy.xml"

cp ${START_FILE} $INPUT_FILE

TO_FIND="ABCDE"


echo 'Looking for input file : ' ${INPUT_FILE}
if [ ! -f ${INPUT_FILE} ]; then
    echo -e "Input data file not found! Please run this file from the unzipped folder downloaded from the Bids website.\n\n"
    exit 1
else
    echo -e "Building Filezilla download queue file.\n\n"
fi

get_user_dir

str1='s*'${TO_FIND}'*'${REPLACE_WITH}'*g'

#echo Full string
#echo $str1
#grep -E ${TO_FIND} ${FILE}

# sed -i -e 's/abc/XYZ/g' /tmp/file.txt
sed -i -e ${str1} ${INPUT_FILE}

echo -e 'Filezilla file created'
echo -e 'To continue, run Filezilla, and select File -> Import and select the xml file in this folder.\n'
read -p "Press enter to close this program." IN_PATH

