#!/bin/bash

log_file="time_log.txt"

for i in {1..8}
do
	printf "simple${i}.txt: "
	python3 -m timeit -n 100 -r 5 'from solution import main; main(["input/simple'"$i"'.txt"])' | tee log/${log_file}
done
