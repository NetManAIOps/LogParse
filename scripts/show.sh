#!/usr/bin/env bash
echo -e "LogTIM script: show the abstract of all results...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
RESULTS_DIR=../results
cd $CURRENT_DIR
. ${CURRENT_DIR}/globalConfig.sh

grep_and_echo()
{
    ALGORITHM=$1
    DATASET=$2
    RATIO=$3
    RETRAIN_LOG=${RESULTS_DIR}/retrain/${ALGORITHM}_${DATASET}_${RATIO}.log
    INCR_LOG=${RESULTS_DIR}/incremental/${ALGORITHM}_${DATASET}_${RATIO}.log

    echo "*****************************"
    echo -e "${ALGORITHM}_${DATASET}_${RATIO}:"

    if [ -f "$RETRAIN_LOG" ]; then
        echo -e "\t*retrain:"
        while read -r line; do
           echo -e "\t\t$line" 
        done < <(grep -E "${GRE_RETRAIN}" "${RETRAIN_LOG}")
    fi

    if [ -f "$INCR_LOG" ]; then
        echo -e "\t*increment:"
        while read -r line; do
           echo -e "\t\t$line" 
        done < <(grep -E "${GRE_LOGTIM}" "${INCR_LOG}")
    fi

    echo -e "\n"
}

while read -r ratio; do
    while read -r algorithm; do
        while read -r dataset; do
            grep_and_echo "$algorithm" "$dataset" "$ratio"
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
done < <(echo -e $RATIO_LIST)
