#!/bin/bash

log_file="time_log.txt"

rm -f log/${log_file}

for i in {1..8}
do
	printf "simple${i}.txt: "
	python3 -m timeit -n 100 'from solution import main; main(["input/simple'"$i"'.txt"])' | tee -a log/${log_file}
done
