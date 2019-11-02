#!/usr/bin/env bash
echo -e "LogTIM script: run for once and just get the results...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
MAIN_DIR=${CURRENT_DIR}/../
cd $MAIN_DIR
. ${CURRENT_DIR}/globalConfig.sh

help_text()
{
    echo -e "USAGE: ./getResults.sh {algorithm} {dataset} {ratio}"
}

ALGORITHM=$1
DATASET=$2
RATIO=$3
LOGTIM_LOG_DIR=results/incremental
[ -z "$ALGORITHM" ] || [ -z "$DATASET" ] || [ -z "$RATIO" ] && help_text && exit 1
[ ! -d "$LOGTIM_LOG_DIR" ] && mkdir $LOGTIM_LOG_DIR

echo -e "algoritm: ${ALGORITHM}"
echo -e "dataset: ${DATASET}"
echo -e "ratio: ${RATIO}"
echo -e "============================"

echo -e "start preprocess"
./splitLog.py -dataset ${DATASET} -ratio ${RATIO} -reprocess false
echo -e "logparse from head data"
./evaluateLogParse.py -dataset ${DATASET} -algorithm ${ALGORITHM} -choose head -ratio ${RATIO} -eval 0 \
    > /dev/null
echo -e "logTIM from tail data"
./logTIM.py ${ALGORITHM} ${DATASET} ${RATIO} 0 \
    > ${LOGTIM_LOG_DIR}/${ALGORITHM}_${DATASET}_${RATIO}.log

echo -e "============================"
echo -e "Finished. Runtime log saved in ${LOGTIM_LOG_DIR}/${ALGORITHM}_${DATASET}_${RATIO}.log"
