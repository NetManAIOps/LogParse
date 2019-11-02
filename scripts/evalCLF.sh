#!/usr/bin/env bash

echo -e "LogTIM script: run classifier evaluation...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
MAIN_DIR=${CURRENT_DIR}/../
cd $MAIN_DIR
. ${CURRENT_DIR}/globalConfig.sh

eval_for_one_ratio()
{
    ratio=$1
    echo -e "Eval for ratio-${ratio}"

    CLF_LOG_DIR=results/classifier
    [ ! -d "$CLF_LOG_DIR" ] && mkdir $CLF_LOG_DIR
    while read -r dataset; do
        ./classifier.py -dataset ${dataset} -ratio ${ratio} \
            > ${CLF_LOG_DIR}/${dataset}_${ratio}.log
    done < <(echo -e $DATASET_LIST)
}

eval_for_one_ratio_multi_thread()
{
    ratio=$1
    echo -e "Eval for ratio-${ratio} [multi-thread]"

    CLF_LOG_DIR=results/classifier
    [ ! -d "$CLF_LOG_DIR" ] && mkdir $CLF_LOG_DIR
    while read -r dataset; do
        ./classifier.py -dataset ${dataset} -ratio ${ratio} \
            > ${CLF_LOG_DIR}/${dataset}_${ratio}.log &
    done < <(echo -e $DATASET_LIST)
    wait
}

if [ "$MULTI_THREAD" -eq "0" ]; then
    while read -r RATIO; do
        eval_for_one_ratio "$RATIO"
    done < <(echo -e $RATIO_LIST)
else
    while read -r RATIO; do
        eval_for_one_ratio_multi_thread "$RATIO"
    done < <(echo -e $RATIO_LIST)
fi
