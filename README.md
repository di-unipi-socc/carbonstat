# CAS: Carbon-Aware Strategies (for containerized services)
To run the current app: 
```
$ docker-compose build
$ docker-compose up
```
Then, you check that different strategies get invoked by repeatedly invoking the service's GET endpoint:
```
$ curl 127.0.0.1:50000
```

## TODOs
* **MUST**: Add invocation to CO2 API to implement the select strategy method
* **MAY**: Add a feature to automatically build the service "stub" based on some config file + service logic