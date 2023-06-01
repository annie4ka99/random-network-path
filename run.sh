#!/bin/bash
INPUT='input/input.txt'
LOG='logs/env.log'
SEED=0
HOST='localhost'
PORT=8000

exec python env/network_application.py --input=$INPUT --log=$LOG --seed=$SEED --host=$HOST --port=$PORT &
sleep 5
exec python agent/path_solver_application.py --network-host=$HOST --network-port=$PORT --seed=$SEED  --max-explore-steps=$1 --stop-after-explore=$2