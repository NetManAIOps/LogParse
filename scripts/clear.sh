#!/usr/bin/env bash
# Be really careful when running this script!
echo -e "LogTIM script: clear results...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
DATA_DIR=../data
RESULTS_DIR=../results
cd $CURRENT_DIR
. ${CURRENT_DIR}/globalConfig.sh

if [ ! -d "${DATA_DIR}" ] && \
    [ ! -d "${RESULTS_DIR}" ]; then
        echo -e "No directory for data or results is found."
        exit 1
fi

DATA_TO_REMOVE=""
RESULT_TO_REMOVE=""

if [ -d "${DATA_DIR}" ]; then 
    DATA_TO_REMOVE=`ls -d -1 ${DATA_DIR}/{*_head_*/,*_tail_*/,*_all/} 2>/dev/null`
    if [ -n "$DATA_TO_REMOVE" ]; then
        DATA_TO_REMOVE=${DATA_TO_REMOVE}"\n"
    fi
fi

if [ -d "${RESULTS_DIR}" ]; then 
    RESULT_TO_REMOVE=`ls -d -1 ${RESULTS_DIR}/{*_results/,incremental/,retrain/,classifier/,logparse/} 2>/dev/null`
    if [ -n "$RESULT_TO_REMOVE" ]; then
        RESULT_TO_REMOVE=${RESULT_TO_REMOVE}"\n"
    fi
fi

if [ ! -n "${DATA_TO_REMOVE}${RESULT_TO_REMOVE}" ]; then
    echo -e "Nothing to remove."
    exit 1
fi

echo -e "${DATA_TO_REMOVE}\n${RESULT_TO_REMOVE}"
echo -e "${RED}Caution: you're going to remove the directories above.${NC}"
echo -n "Enter (y/n) to continue:"

INPUT=""
read INPUT
if [ "$INPUT" != "y" ]; then
    echo "Aborted."
    exit 1
else
    rm -rf ${DATA_DIR}/{*_head_*/,*_tail_*/,*_all/} ${RESULTS_DIR}/{*_results/,incremental/,retrain/,classifier/,logparse/}
    echo "Removed successfully."
    exit 0
fi
