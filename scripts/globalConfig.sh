# DO NOT set interpretor here!

ALGORITHM_LIST="IPLoM\nLogSig\nLKE\nFT_tree\nSpell\nDrain\nMoLFI"
DATASET_LIST="2kBGL\n2kHPC\n2kHDFS\n2kZookeeper\n2kProxifier\n2kHadoop\n2kLinux"
RATIO_LIST="0.1\n0.2\n0.3\n0.4\n0.5\n0.6\n0.7\n0.8\n0.9"

GRE_RETRAIN="precision|recall|RI|F measure|training time"
GRE_LOGTIM="RI|F measure| time|compress rate|new template" 
GRE_VOCAB="number|rate|unmatch"
GRE_CLF="accuracy|recall|f-score|time"
GRE_LOGPARSE="precision|recall|RI|F measure|training time"

GREEN='\033[32m'
RED='\033[0;31m'
NC='\033[0m' 

# 1 for retrain, 0 for not. if EVAL_FLAG is 0, retrain won't happen.
RETRAIN_FLAG=1
# 1 for multi-thread, 0 for not
MULTI_THREAD=1
# 1 for evaluation, 0 for not
EVAL_FLAG=1
