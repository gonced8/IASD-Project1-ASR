#!/bin/bash

log_file="time_log.txt"

touch ${log_file}

for i in {1..8}
do
	printf "simple${i}.txt: "
	python3 -m timeit -n 100 'from solutionv2 import main; main(["input/simple'"$i"'.txt"])' | tee -a ${log_file}
done
