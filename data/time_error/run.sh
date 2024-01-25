#!/bin/bash

# --------------------
#   CONFIGS
# --------------------
# Number of iterations
ITERATIONS=20
RAW_RESULTS=results_raw.csv
AGGREGATED_RESULTS=results.csv

# Clean files 
rm *.log 2> /dev/null
rm *.csv 2> /dev/null

# --------------------
#   RUN
# --------------------
INIT=1
# Repeat for given number of iterations
for i in $(seq $ITERATIONS)
do
    # The very first execution creates the header of the "results_raw.csv" file
    if [ $INIT -eq 1 ]
    then 
        python3 run_strategies.py $RAW_RESULTS --init
        INIT=0
    else
        python3 run_strategies.py $RAW_RESULTS
    fi
done

# Post-process results
python3 post_process.py $RAW_RESULTS $AGGREGATED_RESULTS