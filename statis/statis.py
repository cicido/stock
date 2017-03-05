# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:06:21 2016

@author: Administrator
"""

import pandas as pd
import numpy as np


# data1 = pd.read_csv('loaddata2016_04_27_16_19_47',sep='\t',header=None,names=['s_id','s_name','s_date','s_open','s_high','s_low','s_close','s_vol','s_turnover'],dtype={'s_id':object})
# data2 = pd.read_csv('loaddata2016_04_27_17_12_55',sep='\t',header=None,names=['s_id','s_name','s_date','s_open','s_high','s_low','s_close','s_vol','s_turnover'],dtype={'s_id':object})
# data3 = pd.read_csv('loaddata2016_04_27_18_58_49',sep='\t',header=None,names=['s_id','s_name','s_date','s_open','s_high','s_low','s_close','s_vol','s_turnover'],dtype={'s_id':object})
# data = data1.append(data2).append(data3)
# data = data2.append(data3)
# data = data.sort_values(['s_id','s_date'])
# to avoid index duplication
# data = data.reset_index()

# ma
def ma(N=5):
    return lambda x: x.rolling(window=N).mean()


# ema
def ema(N=12):
    return lambda x: x.ewm(span=N, adjust=False).mean()


# avedev
def avedev(N=14):
    def avedata(x):
        x = x.rolling(window=N).apply(lambda x: abs(x - x.mean()).mean())
        return x

    return avedata


# llv minmum value
def llv(N=14):
    def infunc(x):
        x = x.rolling(window=N).min()
        return x

    return infunc


# hhv maxinum value
def hhv(N=14):
    def infunc(x):
        x = x.rolling(window=N).max()
        return x

    return infunc


# sma
def sma(N=14, M=2):
    def infunc(x):
        x = x.ewm(alpha=float(M) / float(N), adjust=False).mean()
        return x

    return infunc


# sumN
def sumN(N=14):
    return lambda x: x.rolling(window=N).sum()


# countN
def countN(N=14):
    return lambda x: x.rolling(window=N).count()


def stdN(N=14):
    return lambda x: x.rolling(window=N).std()


'''
EMAMEMA: if t<N y(t)=NaN; if t=N y(t)=x[0:N].mean() 
if t>N y(t)=(2*x(t)+(N-1)*y(t-1))/(N+1)
'''


def expmema(N=14):
    def expdata(x):
        x[:N] = x[:N].mean()
        x = x.ewm(span=N, adjust=False).mean()
        x[:N - 1] = np.nan
        return x

    return expdata


def my_cumsum():
    def infunc(x):
        x = x.cumsum()
        return x

    return infunc


def get_resist(N):
    def infunc(x):
        return (x[0] - x[N - 1])

    return infunc


def get_gain(N):
    def infunc(x):
        return (x[N - 1] - x[0]) * 100 / x[0]

    return infunc


def get_gain_sum(N):
    def infunc(x):
        return x.sum()

    return infunc


def get_direct_new(N):
    def bi(m, n):
        return m * 2 + n

    def infunc(x):
        xorder = [1 if x[i] <= x[i + 1] else 0 for i in range(N - 1)]
        # more simple code ,using map and reduce
        return reduce(bi, xorder)

    return infunc


def get_direct(N):
    def infunc(x):
        if x[0] <= x[1]:
            high = 1
        else:
            high = 0
        if x[1] <= x[2]:
            low = 1
        else:
            low = 0
        return high * 2 + low

    return infunc

def get_xor(N):
    def infunc(x):
        if x[0] == x[1]:
            return -1
        elif x[0] < x[1]:
            return 1
        else:
            return 0
    return infunc

def rolling_res(N, func):
    def infunc(x):
        return x.rolling(window=N).apply(func(N))

    return infunc


'''
统一输出行为
'''


def output(s, outcols, indexfile=None):
    s.loc[:, outcols].to_csv(indexfile, float_format='%.3f', index=False)


def ma_statis(indexfile):
    '''
    MA1:MA(CLOSE,M1);
    MA2:MA(CLOSE,M2);
    MA3:MA(CLOSE,M3);
    MA4:MA(CLOSE,M4);
    '''
    print 'computing MA'
    M1 = 5
    M2 = 10
    M3 = 20
    M4 = 60
    s = data[['s_id', 's_date', 's_close']]
    for i in [M1, M2]:
        s.loc[:, 'ma' + str(i)] = s['s_close'].groupby(s['s_id']).transform(ma(i))
        s.loc[:, 'di' + str(i)] = s['ma' + str(i)].groupby(s['s_id']).apply(rolling_res(3, get_direct_new))

    #strategy:

    #  ma5_gt_ma10 = ma5 > ma10  1 else 0
    # 1-> 1 ma5 always larger than ma10, keep stock
    # 1-> 0 ma5 begins less than ma10, sell
    # 0->0 ma5 always less than ma10, keep cash
    # 0->1 ma5 begins larger than ma10, buy
    s.loc[:, 'ma5_gt_ma10'] = 0
    s.loc[s['ma5'] > s['ma10'], 'ma5_gt_ma10'] = 1

    #di_change = -1, like 1->1 or 0->0 ,keep cash or keep stock,just keep
    #di_change = 0, like 1->0 sell
    #di_chnage = 1, like 0->1 buy
    # stategy starts with di_change =  1 and stops with di_change = 0
    s.loc[:,'di_change'] = s['ma5_gt_ma10'].groupby(s['s_id']).apply(rolling_res(2,get_xor))


    cols = ['s_id', 's_date', 's_close', 'ma5', 'ma10', 'di5', 'di10','ma5_gt_ma10','di_change']

    output(s, cols, indexfile)


import os, sys

if __name__ == '__main__':
    datafile = sys.argv[1]
    # sdate = sys.argv[2]

    # basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # basedir = "/data01/stock_index/index_data"
    basedir = sys.argv[2]
    # relmklist = ['MA', 'MACD', 'KDJ', 'RSI', 'GAIN', 'ORI', 'RESIST', 'VOL']
    relmklist = ['MA']
    mkdict = {}
    for i in relmklist:
        mkdict[i] = os.sep.join([basedir, i])

    for i in mkdict.values():
        if not os.path.exists(i):
            try:
                os.mkdir(i)
            except:
                print "mkdir %s failed,exit..." % i
                sys.exit(1)

    relfile = datafile.split(os.sep)[-1]
    print "relfile:", relfile
    cols = ['s_id', 's_name', 's_date', 's_open', 's_high', 's_low', 's_close', 's_vol', 's_turnover']
    data = pd.read_csv(datafile, sep='\t', header=None, names=cols, dtype={'s_id': object})

    print data.shape
    data = data.sort_values(['s_id', 's_date'])
    data = data.reset_index()
    data = data[data.columns[1:]]

    for i in relmklist:
        resfile = os.sep.join([mkdict[i], relfile])
        globals()[i.lower() + '_statis'](resfile)
