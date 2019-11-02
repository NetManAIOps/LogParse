#!/usr/bin/env bash

echo -e "LogTIM script: run the cross evaluation process...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
MAIN_DIR=${CURRENT_DIR}/../
cd $MAIN_DIR
. ${CURRENT_DIR}/globalConfig.sh

preprocess_multi_thread()
{
    echo -e "start preprocess [multi-thread]"

    echo -e "\t*get all dataset"
    while read -r DATASET; do
        ./splitLog.py -dataset ${DATASET} -reprocess false &
    done < <(echo -e $DATASET_LIST)
    wait

    while read -r ALGORITHM; do
        echo -e "\t*logparse with ${ALGORITHM}"
        while read -r DATASET; do
            ./evaluateLogParse.py -dataset ${DATASET} -algorithm ${ALGORITHM} -choose all -eval 0 \
                > /dev/null &
        done < <(echo -e $DATASET_LIST)
        wait
    done < <(echo -e $ALGORITHM_LIST)
}

cross_eval_multi_thread() 
{
    echo -e "start logTIM [multi-thread]"
    
    LOGTIM_LOG_DIR=results/incremental
    [ ! -d "$LOGTIM_LOG_DIR" ] && mkdir $LOGTIM_LOG_DIR

    while read -r ALGORITHM; do
        echo -e "\t*logTIM with templates by ${ALGORITHM}"
        while read -r TRAIN_DATASET; do
            while read -r EVAL_DATASET; do
                if [ "$TRAIN_DATASET" != "$EVAL_DATASET" ]; then
                    ./logTIM.py ${ALGORITHM} ${TRAIN_DATASET} ${EVAL_DATASET} 2 \
                        > ${LOGTIM_LOG_DIR}/${ALGORITHM}_${TRAIN_DATASET}_${EVAL_DATASET}.log &
                fi
            done < <(echo -e $DATASET_LIST)
            wait
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}

preprocess()
{
    echo -e "start preprocess"

    echo -e "\t*get all dataset"
    while read -r DATASET; do
        ./splitLog.py -dataset ${DATASET} -reprocess false
    done < <(echo -e $DATASET_LIST)

    while read -r ALGORITHM; do
        echo -e "\t*logparse with ${ALGORITHM}"
        while read -r DATASET; do
            ./evaluateLogParse.py -dataset ${DATASET} -algorithm ${ALGORITHM} -choose all -eval 0 \
                > /dev/null
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}

cross_eval() 
{
    echo -e "start logTIM"
    
    LOGTIM_LOG_DIR=results/incremental
    [ ! -d "$LOGTIM_LOG_DIR" ] && mkdir $LOGTIM_LOG_DIR

    while read -r ALGORITHM; do
        echo -e "\t*logTIM with templates by ${ALGORITHM}"
        while read -r TRAIN_DATASET; do
            while read -r EVAL_DATASET; do
                if [ "$TRAIN_DATASET" != "$EVAL_DATASET" ]; then
                    ./logTIM.py ${ALGORITHM} ${TRAIN_DATASET} ${EVAL_DATASET} 2 \
                        > ${LOGTIM_LOG_DIR}/${ALGORITHM}_${TRAIN_DATASET}_${EVAL_DATASET}.log
                fi
            done < <(echo -e $DATASET_LIST)
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}


if [ "${MULTI_THREAD}" -eq "1" ]; then
    preprocess_multi_thread
    cross_eval_multi_thread
else
    preprocess
    cross_eval
fi
