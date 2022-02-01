#!/bin/bash

for i in {1..1000}; do
  ./dbgen -vf -s 0.1 -S "$i" -C 1000
done
