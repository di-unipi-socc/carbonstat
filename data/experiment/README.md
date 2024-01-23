# Experiments

TODO:
* write new "experiment.py" that takes as input the csv file to be used as reference
* naive strategy: high power if low carbon (<110) and low request (<333); medium power if moderate carbon (<200) and moderate requests (<666); low power otherwise. Values for carbon taken from carbonintensity; values for requests obtained by dividing 1000 (max reqs) in three chunks