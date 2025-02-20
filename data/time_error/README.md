# Carbonstat

Carbonstat is an open-source prototype for configuring and optimising carbon-aware software services. It selects execution strategies to minimise carbon emissions while maintaining a target quality of service.

Carbonstat methodology is described in the following article:

> [Stefano Forti](http://pages.di.unipi.it/forti), [Jacopo Soldani](http://pages.di.unipi.it/soldani), [Antonio Brogi](http://pages.di.unipi.it/brogi)<br>
> [**Carbon-aware Software Services**](https://doi.org/10.1007/978-3-031-84617-5_6), <br>	
> *11th European Conference On Service-Oriented And Cloud Computing (ESOCC), 2025*

If you wish to reuse source code in this repo, please consider citing it.

## Features of carbonstat
- Implementation based on the Strategy pattern
- Carbon-aware optimization based on forecasted carbon intensity and request rates
- Configurable trade-off between energy consumption and output quality
- Open-source Python prototype using Google OR-Tools
