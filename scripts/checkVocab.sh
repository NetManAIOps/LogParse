#!/usr/bin/env bash
echo -e "LogTIM script: check vocab...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
MAIN_DIR=${CURRENT_DIR}/../
cd $MAIN_DIR
. ${CURRENT_DIR}/globalConfig.sh

check_vocab_and_echo()
{
    ALGORITHM=$1
    DATASET=$2
    RATIO=$3

    echo "*****************************"
    echo -e "${ALGORITHM}_${DATASET}_${RATIO}:"
    ./checkVocab.py -algorithm ${ALGORITHM} -dataset ${DATASET} -ratio ${RATIO} \
        2>/dev/null \
        | grep -E ${GRE_VOCAB}
    echo -e "\n"
}

while read -r ratio; do
    while read -r algorithm; do
        while read -r dataset; do
            check_vocab_and_echo $algorithm $dataset $ratio
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
done < <(echo -e $RATIO_LIST)
