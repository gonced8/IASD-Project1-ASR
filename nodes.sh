#!/bin/bash

log_file="nodes_log.txt"

touch ${log_file}

for i in {1..8}
do
	printf "simple${i}.txt: "
	python3 ./solutionv2.py "input/simple${i}.txt" | tee -a ${log_file}
done
