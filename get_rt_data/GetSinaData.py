# -*- coding: utf-8 -*-
"""
Created on Fri Mar 8 10:53:21 2017

@author: dxp
"""

import os,sys

import urllib2

if __name__ == '__main__':
    id = sys.argv[1]
    prefix = 'sz'
    data = urllib2.urlopen("http://hq.sinajs.cn/list=%s%s" %(prefix,id)).read().decode('cp936')
    if len(data.split(",")) != 33:
        prefix = 'sh'
        data = urllib2.urlopen("http://hq.sinajs.cn/list=%s%s" %(prefix,id)).read().decode('cp936')

    data = data[data.find('"')+1:data.rfind('"')].split(",")
    #print data

    dataArr = data[:30] +[ data[30]+" " +data[31]]
    #print dataArr
    colsName = ['s_name', 's_open','s_last_close','s_current',
                's_high','s_low','s_buy_1','s_sell_1','s_count',
                's_money']
    buyCols = [['s_buy%d_count' %i,'s_buy%d' %i] for i in range(1,6)]
    flattenBuyCols = [ y for x in buyCols for y in x]
    sellCols = [['s_sell%d_count' % i, 's_sell%d' % i] for i in range(1, 6)]
    flattenSellCols = [y for x in sellCols for y in x]
    #colsName = colsName + flattenBuyCols + flattenSellCols + ['datetime']
    colsName = colsName
    #print colsName
    #print len(colsName)
    #print len(dataArr)
    for i in range(len(colsName)):
        print colsName[i] + ":  " + dataArr[i]



