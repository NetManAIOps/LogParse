#!/usr/bin/env bash
echo -e "LogTIM script: restore results from backup...\n"

CURRENT_DIR=`dirname "$0"`
CURRENT_DIR=`cd $CURRENT_DIR; pwd`
RESULTS_DIR=../results
RESULT_BAK_DIR=../result_bak
cd $CURRENT_DIR
. ${CURRENT_DIR}/globalConfig.sh

if [ ! -d "$RESULT_BAK_DIR" ]; then
    echo -e "No backup is found."
    exit 1
fi

count=0
for backup in ${RESULT_BAK_DIR}/results_bak_*.zip
do
    [ "$backup" = "${RESULT_BAK_DIR}/results_bak_*.zip" ] && \
        break
    echo -e "${GREEN}${count}${NC} ${backup}"
    count=$((count+1))
done

if [ "$count" -eq "0" ]; then
    echo -e "No backup is found."
    exit 1
fi

echo -en "\nEnter the index to choose:"
read INPUT

echo ${INPUT:-NULL} | grep "[^0-9]" > /dev/null 2>&1
if [ "$?" -eq "0" ]; then
    echo -e "Aborted."
    exit 1
else
    [ "$INPUT" -ge "$count" ] && \
        echo -e "Aborted." && exit 1

    target=""
    for backup in ${RESULT_BAK_DIR}/results_bak_*.zip
    do
        [ "$INPUT" -eq "0" ] && \
            target=$backup && break
        INPUT=$((INPUT-1))
    done

    echo -e "\n${target} is chosen."
    OPERATION="y"
    if [ -d "$RESULTS_DIR" ]; then
        echo -e "${RED}Caution: the current ${RESULTS_DIR} is going to be replaced.\n${NC}"
        echo -en "Enter (y/n/b) to continue:"
        read OPERATION
    fi

    case "$OPERATION" in
        b)
            ./backup.sh > /dev/null 2>&1
            if [ "$?" -eq "0" ]; then
                echo -e "Backup the current results first."
            else
                echo -e "Backup failed."
                exit 1
            fi

            rm -rf "${RESULTS_DIR}"
            unzip -d ../ ${target} > /dev/null
            echo -e "Restore successfully."
            ;;
        y)
            [ -d "${RESULTS_DIR}" ] && \
                rm -rf "${RESULTS_DIR}"
            unzip -d ../ ${target} > /dev/null
            echo -e "Restore successfully."
            ;;
        *)
            echo "Aborted."
            exit 1
            ;;
    esac
fi

