# Estimating average elapsed time and error of available strategies
This folder provides a set of scripts exemplifying how to measure the elapsed time and error (on average) for the different strategies implemented by a carbon-aware-service. In particular, we provide a concrete example based on the `carbon-aware-service.py` available in this repository.

## Running the estimator
To obtain an esteem of the average time and error of `carbon-aware-service.py` on a given machine, please run the available shell script:
```
./run.sh
```
This will generate two files:
* `results_raw.csv` containing the results obtained by each available strategy in each iteration, and
* `results.csv` containing the average time and error over all iterations.

The number of iterations can be configured by changing the value of the variable `ITERATIONS` within the script `run.sh`. Instead, the number of requests to send to each strategy in each iteration can be configured by changing the value of the variable `requests` in `run_strategies.py`.

## Example of results
An example of the content of the `results.csv` file is provided below:
``` 
strategy,elapsed_time,error
HighPower,100.2091,0.0
MediumPower,66.2948,4.4752
LowPower,35.2861,13.4267
```
This was obtained by running the esteem on a Ubuntu 20.04 LTS virtual machine with 32 GB of RAM.