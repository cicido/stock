#!/bin/bash

if [ $# -ne 3 ];then
    echo "Usage: $0 <datadir> <sdate> <resdir>"
    exit 1
fi

datadir=$1
sdate=$2
resdir=$3
mkdir -p $resdir
ls $datadir > .filecol
while read line
do
    echo $line
    #python over-buy-sell.py $datadir/$line $sdate $resdir
    #python energy.py $datadir/$line $sdate $resdir
    #python trend.py $datadir/$line $sdate $resdir
    #python vol.py $datadir/$line $sdate $resdir 
    #python avg.py $datadir/$line $sdate $resdir
    python index_cal.py $datadir/$line $sdate $resdir
done < .filecol


