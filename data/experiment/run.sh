#!/bin/bash

# --------------------
#   CONFIGS
# --------------------
# Clean logs 
rm *.log 2> /dev/null
# Number of iterations
ITERATIONS=2
# Folder containing the CSV files to be used in the experiment
INPUT_FOLDER=$1
INPUT_FILES=$(ls $INPUT_FOLDER)
# Output files
OUTPUT_FILE=results_$2.csv
OUTPUT_AGG_FILE=results_aggregated_$2.csv

# --------------------
#   RUN
# --------------------
echo "time_slot,policy,total_reqs,carbon,avg_error,max_error" > $OUTPUT_FILE
# Repeat for given number of iterations
for INPUT_FILE in $INPUT_FILES
do
    # Repeat each iteration for each input file
    for i in $(seq $ITERATIONS)
    do
        python3 one_iteration.py $INPUT_FOLDER/$INPUT_FILE $OUTPUT_FILE
    done
    
done

# Post-process results
python3 aggregate_results.py $OUTPUT_FILE $OUTPUT_AGG_FILE