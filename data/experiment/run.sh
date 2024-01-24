#!/bin/bash

# --------------------
#   CONFIGS
# --------------------
# Clean logs 
rm *.log 2> /dev/null
# Number of iterations
ITERATIONS=2
# List of CSV files providing information on the time period to be simulated (separated by ";")
INPUT_FILES_STRING="input/short_example.csv;input/example.csv"
INPUT_FILES=$(echo $INPUT_FILES_STRING | tr ";" "\n")
# CSV file where to put aggregated results
OUTPUT_FILE="results_aggregated.csv"

# --------------------
#   RUN
# --------------------
INIT=1
# Repeat for given number of iterations
for i in $(seq $ITERATIONS)
do
    # Repeat each iteration for each input file
    for INPUT_FILE in $INPUT_FILES
    do
        # The very first execution creates the header of the "results.csv" file
        if [ $INIT -eq 1 ]
        then 
            python3 one_iteration.py $INPUT_FILE results.csv --init
            INIT=0
        else
            python3 one_iteration.py $INPUT_FILE results.csv
        fi
    done
done

# Post-process results
python3 aggregate_results.py results.csv $OUTPUT_FILE