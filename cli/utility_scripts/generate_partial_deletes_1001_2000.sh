#!/bin/bash

dbpath="../data/db_refresh"
for i in {1..1000}; do
  cat $dbpath/orders.tbl.u"$i" | sed -r 's~^([^|]*).*\|(.*)$~\1|~' >> $dbpath/delete."$((i + 1000))"
done
