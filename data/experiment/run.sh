#!/bin/bash

# --------------------
#   CONFIGS
# --------------------
# Clean logs 
rm *.log 2> /dev/null
# Number of iterations
ITERATIONS=2
# Folder containing the CSV files to be used in the experiment
INPUT_FOLDER="error_05" # "example"
INPUT_FILES=$(ls $INPUT_FOLDER)

# --------------------
#   RUN
# --------------------
# Repeat for given number of iterations
for INPUT_FILE in $INPUT_FILES
do
    INIT=1
    # Repeat each iteration for each input file
    for i in $(seq $ITERATIONS)
    do
        # The very first execution creates the header of the "results.csv" file
        if [ $INIT -eq 1 ]
        then 
            python3 one_iteration.py $INPUT_FOLDER/$INPUT_FILE results_$INPUT_FILE --init
            INIT=0
        else
            python3 one_iteration.py $INPUT_FOLDER/$INPUT_FILE results_$INPUT_FILE
        fi
    done
    
    # Post-process results
    python3 aggregate_results.py results_$INPUT_FILE results_aggregated_$INPUT_FILE
done