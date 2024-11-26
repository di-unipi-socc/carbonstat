# carbonstat
To run the current app: 
```
$ docker-compose build
$ docker-compose up
```
Then, you check that different strategies get invoked by repeatedly invoking the service's GET endpoint:
```
$ curl 127.0.0.1:50000
```

## Notes on prototypes
* PolicyMaker gets two CSVs (`timestamp,carbon,reqs` and `strategy,duration,error`) and outputs a CSV (`timestamp,strategy`)
* Carbon-aware service takes CSV `timestamp,strategy` and enforces strategies based on actual time (to be mocked for experiments)

## TODO
* preprocess data with clustering

## Notes
* use pyca as reference of existing source for energy mix
* use M. Aiello et al references for showing that co2 can be measured
* mention that we are inspired by something like approximate computing
* mention/demonstrate "temporal shifting" (in addition to "precision shifting")
* mention that we enable (through query params) to explicitly ask for running the app in full power: `?green=false`
