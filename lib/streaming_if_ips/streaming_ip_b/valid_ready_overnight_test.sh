#!/bin/bash

i=0
rm result.log
for i in `seq 1 10000`
do
  rm log
  #touch log
  valid=$RANDOM
  printf -v valid "%x" "$valid"  
  ready=$RANDOM
  printf -v ready "%x" "$ready"  
  ./scr_streaming_ip_b.py -s -v $valid -r $ready | tee log
  result=`tail -n1 log`
  echo "no.$i valid: $valid ready: $ready - $result"
  echo "no.$i valid: $valid ready: $ready - $result">>result.log 
done
cat result.log
