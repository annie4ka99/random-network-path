## Description
Implementation of Shortest Path search in random graph with Multi-Armed Bandits + Thompson sampling.\
A random lognormal value with unknown parameters is specified for each edge. The distribution parameters are different among edges.\
The agent must find the shortest path in a minimum number of attempts.

## Input format
Put graph parameters into [input/input.txt](input/input.txt) in the following format:
```
<number of nodes> <number of edges>
<start node> <finish node> # nodes are numbered from 0
<from_node> <to_node> <mu> <sigma> # edge parameters line by line
...
```

## Run format
```sh
docker build -t rnp .
docker run -v ./logs:/logs --name=rnp-container rnp
```
- see logs in volume `/logs/env.log` after container is stopped
- to run in test mode without Flask and docker use [test.ipynb](notebooks/test.ipynb)
- see average time plot for requested paths in [test.ipynb](notebooks/test.ipynb)
- change `ENV STEPS` in [Dockerfile](./Dockerfile#L15) to specify max number of running steps 
- change `ENV STOP` in [Dockerfile](./Dockerfile#L14) to stop agent after completing exploration steps (if set to `false`, agent will request paths infinitely) 

