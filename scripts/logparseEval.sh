#!/usr/bin/env bash
echo -e "LogTIM script: run the logparse evaluation...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
MAIN_DIR=${CURRENT_DIR}/../
cd $MAIN_DIR
. ${CURRENT_DIR}/globalConfig.sh

run_for_all_evaluation()
{
    echo -e "\t*start preprocess"
    # split log
    while read -r dataset; do
        ./splitLog.py -dataset ${dataset} -reprocess false
    done < <(echo -e $DATASET_LIST)
    # evaluate all
    while read -r algorithm; do
        echo -e "\t*start ${algorithm}"
        LOGPARSE_LOG_DIR=results/logparse
        [ ! -d "$LOGPARSE_LOG_DIR" ] && mkdir $LOGPARSE_LOG_DIR

        while read -r dataset; do
            ./evaluateLogParse.py -dataset ${dataset} -algorithm ${algorithm} -choose all \
                > ${LOGPARSE_LOG_DIR}/${algorithm}_${dataset}.log
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}

run_for_all_evaluation_multi_thread()
{
    echo -e "\t*start preprocess"
    # split log
    while read -r dataset; do
        ./splitLog.py -dataset ${dataset} -reprocess false &
    done < <(echo -e $DATASET_LIST)
    wait
    # evaluate all
    while read -r algorithm; do
        echo -e "\t*start ${algorithm} [multi-thread]"
        LOGPARSE_LOG_DIR=results/logparse
        [ ! -d "$LOGPARSE_LOG_DIR" ] && mkdir $LOGPARSE_LOG_DIR

        while read -r dataset; do
            ./evaluateLogParse.py -dataset ${dataset} -algorithm ${algorithm} -choose all \
                > ${LOGPARSE_LOG_DIR}/${algorithm}_${dataset}.log &
        done < <(echo -e $DATASET_LIST)
        wait
    done < <(echo -e $ALGORITHM_LIST)
}

if [ "${MULTI_THREAD}" -eq "1" ]; then
    while read -r RATIO; do
        run_for_all_evaluation_multi_thread ${RATIO}
    done < <(echo -e $RATIO_LIST)
else
    while read -r RATIO; do
        run_for_all_evaluation ${RATIO}
    done < <(echo -e $RATIO_LIST)
fi
