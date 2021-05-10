#!/usr/bin/env bash

res=1
retries=0
while [ $res -ne 0 ]
do
  wget $MONGO_HOST:$MONGO_PORT/index.html
  res=$?
done

make flakes-check tests
