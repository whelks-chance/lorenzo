#!/usr/bin/env bash

INPUT_FILE="./CKANFileDownload/FileZilla_Download_Queue2.xml"

# C:\Users\<username>\Documents\filezilla\
TO_FIND="C:\\\\Users\\\\&lt;username&gt;\\\\Documents\\\\filezilla\\\\"

REPLACE_WITH="ABCDE"

#FILE=$1
FILE=${INPUT_FILE}

if [ ! -f ${FILE} ]; then
    echo "File not found!"

else
    echo "Found it"
fi

#echo To Find
#echo ${TO_FIND}
#echo
str1='s/'${TO_FIND}'/'${REPLACE_WITH}'/g'

echo Full string
echo $str1

echo
echo 'grep'
grep -E ${TO_FIND} ${FILE}

# sed -i -e 's/abc/XYZ/g' /tmp/file.txt

echo
echo 'sed'
sed -i -e ${str1} $FILE
