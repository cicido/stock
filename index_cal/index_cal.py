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


def rolling_res(N, func):
    def infunc(x):
        return x.rolling(window=N).apply(func(N))

    return infunc


keycols = ['s_id', 's_date']


def output(s, outcols, indexfile=None):
    s.loc[s['s_date'] >= sdate, keycols + outcols].to_csv(indexfile, float_format='%.3f', index=False)


def ma_index(indexfile):
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
    cols = ['ma' + str(i) for i in [M1, M2]]
    output(s, cols, indexfile)


def macd_index(indexfile):
    print 'computing MACD'
    '''
    DIF:EMA(CLOSE,SHORT)-EMA(CLOSE,LONG);
    DEA:EMA(DIF,MID);
    MACD:(DIF-DEA)*2,COLORSTICK;
    '''
    st = 12
    lg = 26
    mid = 9
    s = data[['s_id', 's_date', 's_close']]
    for i in [st, lg]:
        s.loc[:, 'ema' + str(i)] = s['s_close'].groupby(s['s_id']).transform(ema(i))

    s.loc[:, 'dif'] = s['ema' + str(st)] - s['ema' + str(lg)]
    s.loc[:, 'dea'] = s['dif'].groupby(s['s_id']).transform(ema(mid))
    s.loc[:, 'macd'] = (s['dif'] - s['dea']) * 2
    cols = ['dif', 'dea', 'macd']
    output(s, cols, indexfile)


def kdj_index(indexfile):
    print 'computing KDJ'
    '''
    RSV:=(CLOSE-LLV(LOW,N))/(HHV(HIGH,N)-LLV(LOW,N))*100;
    K:SMA(RSV,M1,1);
    D:SMA(K,M2,1);
    J:3*K-2*D;
    '''
    N = 9
    M1 = 3
    M2 = 3
    s = data[['s_id', 's_date', 's_close', 's_high', 's_low']]
    s.loc[:, 'llv'] = s['s_low'].groupby(s['s_id']).transform(llv(N))
    s.loc[:, 'hhv'] = s['s_high'].groupby(s['s_id']).transform(hhv(N))
    s.loc[:, 'rsv'] = (s['s_close'] - s['llv']) / (s['hhv'] - s['llv']) * 100
    s.loc[:, 'k'] = s['rsv'].groupby(s['s_id']).transform(sma(M1, 1))
    s.loc[:, 'd'] = s['k'].groupby(s['s_id']).transform(sma(M2, 1))
    s.loc[:, 'j'] = s['k'] * 3 - s['d'] * 2
    cols = ['k', 'd', 'j']
    output(s, cols, indexfile)


def rsi_index(indexfile):
    print 'computing RSI'
    '''
    LC:=REF(CLOSE,1);
    RSI1:SMA(MAX(CLOSE-LC,0),N1,1)/SMA(ABS(CLOSE-LC),N1,1)*100;
    RSI2:SMA(MAX(CLOSE-LC,0),N2,1)/SMA(ABS(CLOSE-LC),N2,1)*100;
    RSI3:SMA(MAX(CLOSE-LC,0),N3,1)/SMA(ABS(CLOSE-LC),N3,1)*100;
    '''
    N1 = 6
    N2 = 12
    N3 = 24
    s = data[['s_id', 's_date', 's_close']]
    s.loc[:, 'ref_s_close'] = s['s_close'].groupby(s['s_id']).shift(1)
    s.loc[:, 'maxc_rc'] = 0
    s.loc[:, 'c_sub_rc'] = s['s_close'] - s['ref_s_close']
    s.loc[:, 'maxc_rc'] = s[['maxc_rc', 'c_sub_rc']].max(axis=1)
    s.loc[:, 'absc_rc'] = abs(s['c_sub_rc'])
    s.loc[pd.isnull(s['ref_s_close']), ['maxc_rc', 'absc_rc']] = 0
    for idx, value in enumerate([N1, N2, N3], 1):
        print idx, value
        s.loc[:, 'sma_max_' + str(value)] = s['maxc_rc'].groupby(s['s_id']).transform(sma(value, 1))
        s.loc[:, 'sma_abs_' + str(value)] = s['absc_rc'].groupby(s['s_id']).transform(sma(value, 1))
        s.loc[:, 'rsi' + str(idx)] = s['sma_max_' + str(value)] / s['sma_abs_' + str(value)] * 100
    cols = ['rsi1', 'rsi2', 'rsi3']
    output(s, cols, indexfile)


def gain_index(indexfile):
    '''
    only compute gains and the region
    '''
    print 'computing GAIN'

    s = data[['s_id', 's_date', 's_close']]
    s.loc[:, 'ref_close'] = s["s_close"].groupby(s['s_id']).shift(1)
    s.loc[:, 's_gains'] = (s['s_close'] - s['ref_close']) / s['ref_close'] * 100
    s.loc[:, 't_gains'] = s["s_gains"].groupby(s['s_id']).shift(-1)
    rg = [i + 0.5 for i in range(-11, 11)]
    idrg = range(-10, 11)
    s.loc[:, 's_tag'] = np.nan
    for idx, i in enumerate(rg[1:], 1):
        s.loc[(s['s_gains'] <= rg[idx]) & (s['s_gains'] > rg[idx - 1]), 's_tag'] = idrg[idx - 1]
    s.loc[:, 't_tag'] = s["s_tag"].groupby(s['s_id']).shift(-1)

    cols = ['s_gains', 's_tag', 't_tag']
    output(s, cols, indexfile)


def multgain_index(indexfile):
    '''
    mult days gain, eg:3,5,10,20
    '''
    print 'computing MULTGAIN'
    s = data[['s_id', 's_date', 's_close']]
    s.loc[:, 's_gains'] = s['s_close'].groupby(s['s_id']).apply(rolling_res(2, get_gain))

    # cols = ['s_gains']
    cols = []
    for i in [3, 5, 10, 20]:
        s.loc[:, 's' + str(i)] = s['s_close'].groupby(s['s_id']).apply(rolling_res(i, get_gain))
        cols.append('s' + str(i))
        s.loc[:, 's' + str(i) + '_sum'] = s['s_gains'].groupby(s['s_id']).apply(rolling_res(i, get_gain_sum))
        cols.append('s' + str(i) + '_sum')
        s.loc[:, 's' + str(i) + '_abs_sum'] = np.abs(s['s_gains']).groupby(s['s_id']).apply(
            rolling_res(i, get_gain_sum))
        cols.append('s' + str(i) + '_abs_sum')
    output(s, cols, indexfile)


def ori_index(indexfile):
    '''
    only merge data
    '''

    cols = ['s_id', 's_date', 's_open', 's_high', 's_low', 's_close', 's_vol', 's_turnover']
    s = data[cols]
    cols = cols[2:]
    output(s, cols, indexfile)


def resist_index(indexfile):
    s = data[['s_id', 's_date', 's_close']]
    for i in [2, 5, 10]:
        s.loc[:, 'ma' + str(i) + '_r'] = s['s_close'].groupby(s['s_id']).apply(rolling_res(i, get_resist))
    # s.loc[:,'rsi_r'] = s['ma2_r'].groupby(s['s_id']).apply(rolling_res(6,get_resist))
    s.loc[:, 'rsi_r'] = s['ma2_r'].groupby(s['s_id']).shift(5)
    s.loc[:, 'rsi_r'] = -s['rsi_r']

    cols = ['ma5_r', 'ma10_r', 'rsi_r']
    gain_cols = ['gain_' + i for i in cols]
    for idx, i in enumerate(cols):
        s.loc[:, gain_cols[idx]] = s[i] * 100 / s['s_close']
    rg = [i + 0.5 for i in range(-11, 11)]
    idrg = range(-10, 11)
    s.loc[:, 's_tag'] = np.nan
    tag_cols = [i + '_tag' for i in gain_cols]
    for idx, i in enumerate(rg[1:], 1):
        for j in gain_cols:
            s.loc[(s[j] <= rg[idx]) & (s[j] > rg[idx - 1]), j + '_tag'] = idrg[idx - 1]
    for j in gain_cols:
        s.loc[(s[j] <= rg[0]), j + '_tag'] = -11
        s.loc[(s[j] >= rg[len(rg) - 1]), j + '_tag'] = 11

    cols = gain_cols
    cols.extend(tag_cols)
    output(s, cols, indexfile)


def vol_index(indexfile):
    s = data[['s_id', 's_date', 's_vol']]
    for i in [5, 10]:
        s.loc[:, 'volma' + str(i)] = s.groupby('s_id')['s_vol'].transform(ma(i))
    cols = ['volma' + str(i) for i in [5, 10]]
    output(s, cols, indexfile)


import os, sys

if __name__ == '__main__':
    datafile = sys.argv[1]
    sdate = sys.argv[2]

    # basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    # basedir = "/data01/stock_index/index_data"
    basedir = sys.argv[3]
    relmklist = ['MA', 'MACD', 'KDJ', 'RSI', 'GAIN', 'ORI', 'RESIST', 'VOL']
    # relmklist = ['VOL']
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
    # get file suffix
    suffix = ''
    if sdate != '0':
        suffix = '_' + sdate

    for i in relmklist:
        resfile = os.sep.join([mkdict[i], relfile + suffix])
        globals()[i.lower() + '_index'](resfile)
