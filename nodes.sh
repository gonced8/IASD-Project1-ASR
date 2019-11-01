#!/bin/bash

log_file="nodes_log.txt"

rm -f log/${log_file}

for i in {1..8}
do
	printf "simple${i}.txt: "
	python3 ./solution.py "input/simple${i}.txt" "True" | tee -a log/${log_file}
done
