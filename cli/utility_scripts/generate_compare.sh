#!/bin/bash

dbpath="../data/db_refresh"

# delete od 1 do 1000
for i in {1..1000}; do
  cat $dbpath/delete."$i" >> $dbpath/b.txt
  cat $dbpath/orders.tbl.u"$((i + 1000))" | sed -r 's~^([^|]*).*\|(.*)$~\1|~' >> $dbpath/a.txt
done

# delete od 1001 do 2000
for i in {1..1000}; do
  cat $dbpath/delete."$((i + 1000))" >> $dbpath/b.txt
  cat $dbpath/orders.tbl.u"$i" | sed -r 's~^([^|]*).*\|(.*)$~\1|~' >> $dbpath/a.txt
done