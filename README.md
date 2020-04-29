# Paper

Our paper is published on The 29th International Conference on Computer Communications and Networks 
([ICCCN 2020](http://www.icccn.org/icccn20/),). The information can be found here:

* **LogParse: Making Log Parsing Adaptive through Word Classification**. Weibin Meng, Ying Liu, Federico Zaiter, Shenglin Zhang, Yihao Chen, Yuzhe Zhang, Yichen Zhu, En Wang, Ruizhi Zhang, Shimin Tao, Dian Yang, Rong Zhou, Dan Pei. ICCCN 2020. August 3 - August 6, 2020, Honolulu, Hawaii, USA.


Quick Start
===

```bash
# clear the results
./scripts/clear.sh

# split all the data
./scripts/split.sh

# run for once and get results without evaluation
./scripts/getResults.sh {ALGORITHM} {DATASET} {RATIO}

# run the whole process
./scripts/run.sh

# run the cross evaluation process
./scripts/crossEval.sh

# check the vocab
./scripts/checkVocab.sh

# evaluate classifier
./scripts/evalCLF.sh

# evaluate logparse
./scripts/logparseEval.sh

# show the abstract of current ./results/
./scripts/show.sh

# make a back up of current results to ./result_bak/
./scripts/backup.sh

# restore results from .zip file in the ./result_bak/
./scripts/restore.sh

# export the summary of all results in .csv file
./scripts/export.sh {PATH/TO/EXPORT}
```
Directory Structure
===
```bash
.
|-- algorithm
|   |-- Drain.py
|   |-- ft_tree/
|   |-- IPLoM.py
|   |-- LKE/
|   |-- LogSig.py
|   |-- MoLFI/
|   `-- Spell.py
|
|-- checkVocab.py
|-- classifier.py
|-- compressRate.py
|-- DESCRIPTION.md
|-- data
|   |-- 2kBGL/
|   |-- 2kHadoop/
|   |-- 2kHDFS/
|   |-- 2kHPC/
|   |-- 2kLinux/
|   |-- 2kProxifier/
|   |-- 2kZookeeper/
|   |-- countTempalates.py
|   `-- datasets.zip
|
|-- evaluateLogParse.py
|-- getVocab.py
|-- globalConfig.py
|-- logTIM.py
|-- matchTree.py
|-- README.md
|-- result_bak/
|-- results/
|-- retrain.py
|-- RI_precision.py
|-- scripts
|   |-- backup.sh
|   |-- checkVocab.sh
|   |-- clear.sh
|   |-- crossEval.sh
|   |-- evalCLF.sh
|   |-- export.sh
|   |-- getResults.sh
|   |-- globalConfig.sh
|   |-- logparseEval.sh
|   |-- restore.sh
|   |-- run.sh
|   |-- show.sh
|   `-- split.sh
|
`-- splitLog.py
```

How To
===
### How to add new dataset?
to add a new dataset named 'Sample'
1. create a dir as `./data/Sample/`
2. put the `rawlog.log` file in `./data/Sample/`
3. (optional) put the `groundtruth.seq` file in `./data/Sample/`. only with this file can you evaluate the results.
4. modify the file `globalConfig.py`, add all the needed configurations.
5. (optional) modify the file `scripts/globalConfig.sh`, add all the needed configurations, if you want to run scripts.

File Descriptions
===

### globalConfig.py
**Description:** global configurations for all python scripts.

**Usage:** insert `from globalConfig import *` in every concerned python files.

> **What Is Set Here**
>
> Global paths:
> * DATA_PATH -- path to the data directory, typically "./data/".
> * RESULT_PATH -- path to the result directory, typically "./results/".
> * ALGORITHM_PATH -- path to the algorithm directory, typically "./algorithm/".
>
> Enum objects:
> * ALGORITHM_LIST -- list of all the algorithm names.
> * DATASET_LIST -- list of all the dataset names.
> * ALGORITHM_STR -- string of all the algorithm names, mainly used for help instructions.
> * DATASET_STR -- string of all the dataset names, mainly used for help instructions.
>
> Others:
> * ContextNum -- a dictionary to set the number of words in the preceding context and succeeding context when training classifier.
> * regL -- a dictionary to set the regular rules, which would be used to clean the log text.
> * removeCol -- a dictionary to set the columns to be removed in a dataset.
> * GroupNum -- a dictionary to set the parameter groupNum in LogSig algorithm

**Note: when new algorithm or new dataset is added, remember to modify the configurations in this file.**
___
### splitLog.py
**Description:** split data to different partions in specific ratio.

**Usage:** `./splitLog.py [-dataset {DATASET}] [-ratio {RATIO}] [-reprocess {REPROCESS_FLAG}]`

> * dataset -- one of the items in the DATASET_LIST, which is set in `globalConfig.py`. Default is '2kBGL'
> * ratio -- the ratio for _head data. Default is '0.5'.
> * reprocess -- flag to reprocess the _all data even if it already existed. Default is 'False'.

**Note: typically, run `./splitLog.py -dataset 2kBGL -ratio 0.1 -reprocess True` will create `./data/2kBGL_head_0.10/`, `./data/2kBGL_tail_0.10/` and `./data/2kBGL_all/`, where stores, respectively, the first 0.1, the last 0.9 and all of the 2kBGL data, with text cleaned and columns removed.**
___
### evaluateLogParse.py
**Description:** run logparse algorithm, save the results and evaluate them.

**Usage:** `./evaluateLogParse.py [-dataset {DATASET}] [-algorithm {ALGORITHM}] [-choose {PART}] [-ratio {RATIO}] [-eval {EVAL_FLAG}]`

> * dataset -- one of the items in the DATASET_LIST, which is set in `globalConfig.py`. Default is '2kBGL'
> * algorithm -- one of the items in the ALGORITHM_LIST, which is set in `globalConfig.py`. Default is 'LKE'
> * choose -- the part of dataset to choose, in 'head, tail, all'. Default is 'head'.
> * ratio -- the ratio for _head data. Default is '0.5'. when running with cross evaluation, this parameter is target dataset name.
> * eval -- the flag to decide whether to evaluate. Default is '1'

**Note: typically, run `./evaluateLogParse.py -dataset 2kBGL -algorithm FT_tree -choose head -ratio 0.1` will store the results in `./results/FT_tree_results/2kBGL_head_0.10/`, which will used for logTIM's training.**
___
### logTIM.py
**Description:** use parsed results to train word classifier, match new logs and incrementally add new templates. 

**Usage:** `./logTIM.py {ALGORITHM} {DATASET} {RATIO} {EVAL_FLAG}`

> * ALGORITHM -- one of the items in the ALGORITHM_LIST, which is set in `globalConfig.py`
> * DATASET -- one of the items in the DATASET_LIST, which is set in `globalConfig.py`
> * RATIO -- the ratio for _head data (trainning data). for cross evaluation, this parameter send the name of target dataset
> * EVAL_FLAG -- the flag to decide how to evaluate (0 for no evaluation, 1 for internal evaluation, 2 for cross evaluation)

**Note: typically, run `./logTIMpy FT_tree 2kBGL 0.1 1` will store the results in `./results/logTIM_results/FT_tree_results/2kBGL_0.10/`, where `matchResults.txt` and `logTemplates.txt` are what you may be interested in.**

**Note: for cross evaluaton, run `./logTIMpy FT_tree 2kBGL 2kHPC 2` will use the whole 2kBGL as training data, and then match and evaluate on the 2kHPC dataset. it will store the results in `./results/logTIM_results/FT_tree_results/2kBGL_TO_2kHPC/`.**
___
### compressRate.py
**Description:** calculate compress rate

**Usage:** `from compressRate import compressRate`, which is a function used in logTIM.py

**Note:  before calling this function, be sure there is `matchResults.txt` and `rawlog.txt` of the tail part of specific ratio. You can check its usage in logTIM.py**
___
### matchTree.py
**Description:** tree structure for template match

**Usage:** `from matchTree import *`, which imports the MatchTree class used in logTIM.py and checkVocab.py
___
### RI_precision.py
**Description:** evaluate RI precision

**Usage:** `from RI_precision import *`, which imports the evaluation functions used in logTIM.py, retrain.py and evaluateLogParse.py

**Note: the evaluation function will accept results path and groundtruth data path as parameters, and calculate RI precision from them. So be careful of the format of the results and groundtruth data.**
___
### getVocab.py
**Description:** get vocabulary for classifier

**Usage:** `from getVocab import *`, which imports the help functions used in logTIM.py and classifier.py
___
### retrain.py
**Description:** evaluate retrain results

**Usage:** `./retrain.py {ALGORITHM} {DATASET} {RATIO}`

> * ALGORITHM -- one of the items in the ALGORITHM_LIST, which is set in `globalConfig.py`
> * DATASET -- one of the items in the DATASET_LIST, which is set in `globalConfig.py`
> * RATIO -- the ratio for _head data

**Note: you may not want to run this because we find retrain evaluation is not reasonable in some way. Check `./scripts/retrain.sh` to see how to run it if you really want to.**
___
### checkVocab.py
**Description:** find the template-as-well-as-variable vocab

**Usage:** `./checkVocab.py [-dataset {DATASET}] [-algorithm {ALGORITHM}] [-save {SAVEPATH}] [-ratio {RATIO}]`

> * dataset -- one of the items in the DATASET_LIST, which is set in `globalConfig.py`. Default is '2kBGL'
> * algorithm -- one of the items in the ALGORITHM_LIST, which is set in `globalConfig.py`. Default is 'IPLoM'
> * save -- the directory to save temporary files. Default is ''.
> * ratio -- the ratio for _head data. Default is '0.5'.

**Note: typically, run `./checkVocab.py -dataset 2kBGL -algorithm FT_tree -ratio 0.1` will check the template-as-well-as-variable vocab for the results of logTIM with the setting of FT_tree/2kBGL/0.1. Before running, be sure there is `logTemplates.txt` in the specific logTIM results directory**
___
### classifier.py
**Description:** train vocab classifier

**Usage1:** `from classifier import *`, which imports the data_loader and SVM functions used in logTIM.py

**Usage2:** run `./classifier.py [-dataset {DATASET}] [-ratio {RATIO}] [-preceding {PRECEDING}] [-succeeding {SUCCEEDING}]` to evaluate the classifier

> * dataset -- one of the items in the DATASET_LIST, which is set in `globalConfig.py`. Default is '2kBGL'
> * ratio -- the ratio for training data. Default is '0.5'.
> * preceding -- preceding word number in context. Default is '-1'.
> * succeeding -- succeeding word number in context. Default is '-1'.

**Note: typically, run `./classifier.py -dataset 2kBGL -ratio 0.1` will use the `ContextNum` set in `globalConfig.py` to choose context word numbers, and use the first 0.1 of the data to train the classifier and use the last 0.9 of the data to evaluate.**

___
### logFilter.py
**Description:** preprocess rawlog data, remove invlid lines

**Usage:** run `./logFilter.py [-input {INPUT_PATH}] [-output {OUTPUT_PATH}]`

> * input -- path to the rawlog file. Default is 'rawlog.log'
> * output -- path to store output file. Default is 'rawlog.log.after'

**Note: this script is used to filter the rawlogs more specifically at a line's scale, e.g. remove the lines that do not match with some regluar rules. this is not run with logTIM and you should manually set the configuration within this file before running it. Typically, run this script with Hadoop log file to remove the sublines of a multi-line log in Hadoop rawlog file.**

<font color=gray size=5>This code was completed by Weibin Meng, Yihao Chen and Yuzhe Zhang in cooperation.</font>
