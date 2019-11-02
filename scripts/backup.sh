#!/usr/bin/env bash
echo -e "LogTIM script: make results backup...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
RESULTS_DIR=../results
RESULT_BAK_DIR=../result_bak
cd $CURRENT_DIR

if [ ! -d "$RESULTS_DIR" ]; then
    echo -e "No result directory found."
    exit 1
fi

[ ! -d "$RESULT_BAK_DIR" ] && \
    mkdir $RESULT_BAK_DIR

BAK_NAME=results_bak_$(date +%Y_%m_%d_%H:%M:%S).zip
zip -r ${RESULT_BAK_DIR}/${BAK_NAME} ${RESULTS_DIR} > /dev/null

if [ "$?" -eq "0" ]; then
    echo -e "Backup successfully: ${BAK_NAME}"
else
    echo -e "Zip failed."
    exit 1
fi
