#!/usr/bin/env bash
echo -e "LogTIM script: run the whole process...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
MAIN_DIR=${CURRENT_DIR}/../
cd $MAIN_DIR
. ${CURRENT_DIR}/globalConfig.sh

run_for_one_ratio()
{
    ratio=$1
    evalflag=$2
    retrainflag=$3
    echo -e "Run for ratio-${ratio}:"

    echo -e "\t*start preprocess"
    # split log
    while read -r dataset; do
        ./splitLog.py -dataset ${dataset} -ratio ${ratio} -reprocess false
    done < <(echo -e $DATASET_LIST)
    # head process
    while read -r algorithm; do
        while read -r dataset; do
            ./evaluateLogParse.py -dataset ${dataset} -algorithm ${algorithm} -choose head -ratio ${ratio} -eval 0 \
                > /dev/null
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)

    # retrain and logTIM
    while read -r algorithm; do
        echo -e "\t*start ${algorithm}"
        # retrain if RETRAN_FLAG set to 1
        if [ "$retrainflag" -eq "1" ] && [ "$evalflag" -eq "1" ]; then
            RETRAIN_LOG_DIR=results/retrain
            [ ! -d "$RETRAIN_LOG_DIR" ] && mkdir $RETRAIN_LOG_DIR

            while read -r dataset; do
                ./evaluateLogParse.py -dataset ${dataset} -algorithm ${algorithm} -choose all \
                    > ${RETRAIN_LOG_DIR}/${algorithm}_${dataset}_${ratio}.log
                ./retrain.py ${algorithm} ${dataset} ${ratio} \
                    >> ${RETRAIN_LOG_DIR}/${algorithm}_${dataset}_${ratio}.log
            done < <(echo -e $DATASET_LIST)
        fi
        # logTIM
        LOGTIM_LOG_DIR=results/incremental
        [ ! -d "$LOGTIM_LOG_DIR" ] && mkdir $LOGTIM_LOG_DIR
        
        while read -r dataset; do
            ./logTIM.py ${algorithm} ${dataset} ${ratio} ${evalflag} \
                > ${LOGTIM_LOG_DIR}/${algorithm}_${dataset}_${ratio}.log
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}

run_for_one_ratio_multi_thread()
{
    ratio=$1
    evalflag=$2
    retrainflag=$3
    echo -e "Run for ratio-${ratio} [multi-thread]:"

    echo -e "\t*start preprocess"
    # split log
    while read -r dataset; do
        ./splitLog.py -dataset ${dataset} -ratio ${ratio} -reprocess false &
    done < <(echo -e $DATASET_LIST)
    wait
    # head process
    while read -r algorithm; do
        while read -r dataset; do
            ./evaluateLogParse.py -dataset ${dataset} -algorithm ${algorithm} -choose head -ratio ${ratio} -eval 0 \
                > /dev/null &
        done < <(echo -e $DATASET_LIST)
        wait
    done < <(echo -e $ALGORITHM_LIST)

    # retrain and logTIM
    while read -r algorithm; do
        echo -e "\t*start ${algorithm}"
        # retrain if RETRAN_FLAG set to 1
        if [ "$retrainflag" -eq "1" ] && [ "$evalflag" -eq "1" ]; then
            RETRAIN_LOG_DIR=results/retrain
            [ ! -d "$RETRAIN_LOG_DIR" ] && mkdir $RETRAIN_LOG_DIR

            while read -r dataset; do
                ./evaluateLogParse.py -dataset ${dataset} -algorithm ${algorithm} -choose all \
                    > ${RETRAIN_LOG_DIR}/${algorithm}_${dataset}_${ratio}.log && \
                ./retrain.py ${algorithm} ${dataset} ${ratio} \
                    >> ${RETRAIN_LOG_DIR}/${algorithm}_${dataset}_${ratio}.log &
            done < <(echo -e $DATASET_LIST)
            wait
        fi
        # logTIM
        LOGTIM_LOG_DIR=results/incremental
        [ ! -d "$LOGTIM_LOG_DIR" ] && mkdir $LOGTIM_LOG_DIR
        
        while read -r dataset; do
            ./logTIM.py ${algorithm} ${dataset} ${ratio} ${evalflag} \
                > ${LOGTIM_LOG_DIR}/${algorithm}_${dataset}_${ratio}.log &
        done < <(echo -e $DATASET_LIST)
        wait
    done < <(echo -e $ALGORITHM_LIST)
}

if [ "${MULTI_THREAD}" -eq "1" ]; then
    while read -r RATIO; do
        run_for_one_ratio_multi_thread ${RATIO} ${EVAL_FLAG} ${RETRAIN_FLAG}
    done < <(echo -e $RATIO_LIST)
else
    while read -r RATIO; do
        run_for_one_ratio ${RATIO} ${EVAL_FLAG} ${RETRAIN_FLAG}
    done < <(echo -e $RATIO_LIST)
fi
