#!/bin/bash

if [ $# -ne 2 ];then
    echo "Usage: $0 <datafile> <dstdir>"
    exit 1
fi

datafile=$1
dstdir=$2
:>.plate
:>.stock
awk '{a[substr($1,1,4)]++}END{for(i in a) print i}'  $datafile >.idlist
awk '$1~/^88/{print $0 > ".plate";next}{print $0 > ".stock"}END{close(".plate");close(".stock")}' .idlist
mkdir -p $dstdir/"plate"
mkdir -p $dstdir/"stock"
while read line
do
    echo $line
    awk '$1~/^'"$line"'/' $datafile >> $dstdir/"plate"/$line
done < .plate

while read line
do
    echo $line
    awk '$1~/^'"$line"'/' $datafile >> $dstdir/"stock"/$line
done < .stock
