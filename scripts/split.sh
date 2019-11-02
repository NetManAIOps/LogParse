#!/usr/bin/env bash
echo -e "LogTIM script: run the split process...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
MAIN_DIR=${CURRENT_DIR}/../
cd $MAIN_DIR
. ${CURRENT_DIR}/globalConfig.sh

split_for_one_ratio()
{
    ratio=$1
    echo -e "Split for ratio-${ratio}"
    while read -r dataset; do
        ./splitLog.py -dataset ${dataset} -ratio ${ratio} -reprocess false
    done < <(echo -e $DATASET_LIST)
}

split_for_one_ratio_multi_thread()
{
    ratio=$1
    echo -e "Split for ratio-${ratio} [multi-thread]"
    while read -r dataset; do
        ./splitLog.py -dataset ${dataset} -ratio ${ratio} -reprocess false &
    done < <(echo -e $DATASET_LIST)
    wait
}

if [ "${MULTI_THREAD}" -eq "1" ]; then
    while read -r RATIO; do
        split_for_one_ratio_multi_thread ${RATIO}
    done < <(echo -e $RATIO_LIST)
else
    while read -r RATIO; do
        split_for_one_ratio ${RATIO}
    done < <(echo -e $RATIO_LIST)
fi

echo -e "Success."
