#!/bin/bash

log_file="stats_log.txt"

rm -f log/${log_file}

for i in {1..8}
do
	echo "simple${i}.txt"
	python3 ./solution.py "input/simple${i}.txt" 1 1 1 | tee log/${log_file}
	echo ""
done
