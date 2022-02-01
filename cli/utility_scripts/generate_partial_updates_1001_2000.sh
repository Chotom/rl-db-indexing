#!/bin/bash

prdata="../data/par_data"
dbpath="../data/db_refresh"
for i in {1..1000}; do
  cat $prdata/orders.tbl."$i" >> $dbpath/orders.tbl.u"$((i + 1000))"
done
