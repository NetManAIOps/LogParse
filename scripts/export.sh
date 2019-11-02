#!/usr/bin/env bash
echo -e "LogTIM script: export .csv file of all results...\n"

WORKING_DIR=`pwd`
CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
RESULTS_DIR=../results
cd $CURRENT_DIR
. ${CURRENT_DIR}/globalConfig.sh

grep_and_export_incr_csv_line()
{
    ALGORITHM=$1
    DATASET=$2
    RATIO=$3
    INCR_LOG=${RESULTS_DIR}/incremental/${ALGORITHM}_${DATASET}_${RATIO}.log

    if [ ! -f "$INCR_LOG" ]; then
        return 1
    fi
    LINE="${ALGORITHM}_${DATASET}_${RATIO}"
    REGX="([0-9.]+)"
    while read -r line; do
        if [[ $line =~ $REGX ]]; then
            value="${BASH_REMATCH[1]}"
            LINE="$LINE""\t""$value"
        fi
    done < <(grep -E "${GRE_LOGTIM}" "${INCR_LOG}")
    echo -e "$LINE"
}

grep_and_export_retrain_csv_line()
{
    ALGORITHM=$1
    DATASET=$2
    RATIO=$3
    RETRAIN_LOG=${RESULTS_DIR}/retrain/${ALGORITHM}_${DATASET}_${RATIO}.log

    if [ ! -f "$RETRAIN_LOG" ]; then
        return 1
    fi

    LINE="${ALGORITHM}_${DATASET}_${RATIO}_RETRAIN"
    REGX="([0-9.]+)"
    while read -r line; do
        if [[ $line =~ $REGX ]]; then
            value="${BASH_REMATCH[1]}"
            LINE="$LINE""\t""$value"
        fi
    done < <(grep -E "${GRE_RETRAIN}" "${RETRAIN_LOG}")
    echo -e "$LINE"
}

grep_and_export_clf_csv_line()
{
    DATASET=$1
    RATIO=$2
    CLF_LOG=${RESULTS_DIR}/classifier/${DATASET}_${RATIO}.log

    if [ ! -f "$CLF_LOG" ]; then
        return 1
    fi

    LINE="${DATASET}_${RATIO}_CLF"
    REGX="([0-9.]+)"
    while read -r line; do
        if [[ $line =~ $REGX ]]; then
            value="${BASH_REMATCH[1]}"
            LINE="$LINE""\t""$value"
        fi
    done < <(grep -E "${GRE_CLF}" "${CLF_LOG}")
    echo -e "$LINE"
}

grep_and_export_logparse_csv_line()
{
    DATASET=$1
    ALGORITHM=$2
    LOGPARSE_LOG=${RESULTS_DIR}/logparse/${ALGORITHM}_${DATASET}.log

    if [ ! -f "$LOGPARSE_LOG" ]; then
        return 1
    fi

    LINE="${DATASET}_${ALGORITHM}_LOGPARSE"
    REGX="([0-9.]+)"
    while read -r line; do
        if [[ $line =~ $REGX ]]; then
            value="${BASH_REMATCH[1]}"
            LINE="$LINE""\t""$value"
        fi
    done < <(grep -E "${GRE_LOGPARSE}" "${LOGPARSE_LOG}")
    echo -e "$LINE"
}

export_incr_csv()
{
    TO_PATH="$1"
    while read -r algorithm; do
        while read -r dataset; do
            while read -r ratio; do
                grep_and_export_incr_csv_line "$algorithm" "$dataset" "$ratio" \
                    >> "$TO_PATH"
            done < <(echo -e $RATIO_LIST)
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}

export_retrain_csv()
{
    TO_PATH="$1"
    while read -r algorithm; do
        while read -r dataset; do
            while read -r ratio; do
                grep_and_export_retrain_csv_line "$algorithm" "$dataset" "$ratio" \
                    >> "$TO_PATH"
            done < <(echo -e $RATIO_LIST)
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}

export_clf_csv()
{
    TO_PATH="$1"
    while read -r dataset; do
        while read -r ratio; do
            grep_and_export_clf_csv_line "$dataset" "$ratio" \
                >> "$TO_PATH"
        done < <(echo -e $RATIO_LIST)
    done < <(echo -e $DATASET_LIST)
}

export_cross_eval_csv()
{
    TO_PATH="$1"
    while read -r algorithm; do
        while read -r train_dataset; do
            while read -r eval_dataset; do
                if [ "$train_dataset" != "$eval_dataset" ]; then
                    grep_and_export_incr_csv_line "$algorithm" "$train_dataset" "$eval_dataset" \
                        >> "$TO_PATH"
                fi
            done < <(echo -e $DATASET_LIST)
        done < <(echo -e $DATASET_LIST)
    done < <(echo -e $ALGORITHM_LIST)
}

export_logparse_csv()
{
    TO_PATH="$1"
    while read -r dataset; do
        while read -r algorithm; do
            grep_and_export_logparse_csv_line "$dataset" "$algorithm" \
                >> "$TO_PATH"
        done < <(echo -e $ALGORITHM_LIST)
    done < <(echo -e $DATASET_LIST)
}

SAVE_PATH=${1:-result_summary.csv}
if [[ ! "$SAVE_PATH" = /* ]]; then
    SAVE_PATH=${WORKING_DIR}/${SAVE_PATH}
fi 

if [ -d "$SAVE_PATH" ]; then
    echo -e "Path to a directory already exists, script aborted."
    exit 1
fi

echo -e "Which part do you want to export?\n"
echo -e "${GREEN}0${NC} Incremental"
echo -e "${GREEN}1${NC} Retrain"
echo -e "${GREEN}2${NC} Classifier"
echo -e "${GREEN}3${NC} Logparse"
echo -e "${GREEN}4${NC} Cross evaluation"
echo -e ""
echo -en "Enter the index to continue:"
read INDEX

if [ "$INDEX" !=  "0" ] && \
    [ "$INDEX" != "1" ] && \
    [ "$INDEX" != "2" ] && \
    [ "$INDEX" != "3" ] && \
    [ "$INDEX" != "4" ]; then
    echo -e "Aborted."
    exit 1
fi

if [ -f "$SAVE_PATH" ]; then
    echo -e "${RED}Caution: file ${SAVE_PATH} already exists\n${NC}"
    echo -en "Enter (y/n) to continue:"
    read INPUT
    if [ "$INPUT" = "y" ]; then
        rm "$SAVE_PATH"
    else
        echo -e "Aborted."
        exit 1
    fi
fi

touch "$SAVE_PATH" > /dev/null 2>&1
if [ ! "$?" -eq "0" ]; then
    echo -e "Failed to create file."
    exit 1
fi

case "$INDEX" in
    0)
        echo -e "Export incremental..."
        export_incr_csv "$SAVE_PATH"
        ;;
    1)
        echo -e "Export retrain..."
        export_retrain_csv "$SAVE_PATH"
        ;;
    2)
        echo -e "Export classifier..."
        export_clf_csv "$SAVE_PATH"
        ;;
    3)
        echo -e "Export logparse..."
        export_logparse_csv "$SAVE_PATH"
        ;;
    4)
        echo -e "Export cross evaluation..."
        export_cross_eval_csv "$SAVE_PATH"
        ;;
    *)
        echo -e "Should have been aborted earlier."
        exit 2
        ;;
esac

echo -e "Export successfully."
