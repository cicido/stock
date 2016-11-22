# -*- coding: utf-8 -*-
"""
Created on Sat Jun 04 19:16:22 2016

@author: Administrator
"""

import pandas as pd
import numpy as np
import os,sys

def output(data,resfile):
    if sdate == '0':
        data.to_csv(resfile,float_format='%.3f',index=False)
    else:
        data[(data['s_date'] == sdate)].to_csv(resfile,float_format='%.3f',index=False)

def get_direct(N):
    def infunc(x):
        if x[0]<=x[1]:
            high = 1
        else:
            high = 0
        if x[1]<= x[2]:
            low = 1
        else:
            low = 0
        return high*2 + low
    return infunc

def cal_dif(N):
    def infunc(x):
        return abs(x[0]-x[N-1])/x[N-1]
    return infunc

def rolling_res(N,func):
    def infunc(x):
        return x.rolling(window=N).apply(func(N))
    return infunc
    
def cal_direct(data,index,cols):
    cols_d = [index+'_'+i+'_d' for i in cols]
    for idx,i in enumerate(cols):
        data[cols_d[idx]] = data.groupby(data['s_id'])[i].apply(rolling_res(3,get_direct))

def ori_chose(resfile):
    s.loc[:,'max'] = s[['s_open','s_close']].max(axis=1)
    s.loc[:,'min'] = s[['s_open','s_close']].min(axis=1)
    s.loc[:,'high_max'] = s['s_high']-s['max']
    s.loc[:,'min_low'] = s['min'] - s['s_low']
    s.loc[:,'max_min'] = s['max'] - s['min']
    for i in ['s_close']:
        s.loc[:,i+'_d'] = s[i].groupby(s['s_id']).apply(rolling_res(3,get_direct))
    #chose hammer state
    pdata = s[(s['min_low']>2*s['max_min']) &(s['high_max']<0.5*s['max_min'])]
    output(pdata,resfile+'_hammer_positive')
    #chose ten character state
    pdata = s[(s['min_low']>2*s['max_min']) &(s['high_max']>2*s['max_min'])]
    output(pdata,resfile+'_ten_positive')
    
    #chose ma5,ma10
    for i in [5,10]:
        s.loc[:,'dif_'+str(i)] = s['s_close'].groupby(s['s_id']).apply(rolling_res(i,cal_dif))
    pdata = s
    output(pdata,resfile+"madiff_positive")

    #chose less
    s.loc[:,'less'] = s['s_close'].groupby(s['s_id']).apply(rolling_res(6,cal_dif))
    pdata = s
    output(pdata,resfile + "rsidiff_positive")

def gain_chose(resfile):
    '''
    mainly for merge data
    '''
    pdata = s
    output(pdata,resfile+'_positive')
    
def ma_chose(resfile):
    for i in ['ma1','ma2','ma3','ma4']:
        s.loc[:,i+'_d'] = s[i].groupby(s['s_id']).apply(rolling_res(3,get_direct))
    #chose
    output(s,resfile+'_merge')
    pdata = s[(s['ma1_d'] == 1)]
    output(pdata,resfile+'_positive')

def macd_chose(refile):
    for i in ['dif']:
        s.loc[:,i+'_d'] = s[i].groupby(s['s_id']).apply(rolling_res(3,get_direct))
    #chose
    pdata = s[(s['dif_d'] == 1)]
    output(pdata,resfile+'_positive')
            
def cci_chose(resfile):
    for i in ['cci']:
         s.loc[:,i+'_d'] = s[i].groupby(s['s_id']).apply(rolling_res(3,get_direct))
    #chose
    pdata = s[(s['cci_d'] > 0)]
    output(pdata,resfile+'_positive')
    

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print "Usage:" + ' '.join([sys.argv[0],'<datadir>','<resdir>','<index>','<sdate>'])
        sys.exit(1)

    datadir= sys.argv[1]
    resdir = sys.argv[2]
    index= sys.argv[3]
    sdate = sys.argv[4]

    index_dir = os.sep.join([datadir,index])
    relfilelist = [ i for i in os.listdir(index_dir) if os.path.isfile(os.sep.join([index_dir,i]))]
    #print relfilelist
    s = pd.DataFrame()
     
    for i  in relfilelist:
        idxfile = os.sep.join([index_dir,i])
        #print idxfile
        if s.empty:
            s = pd.read_csv(idxfile,dtype={'s_id':object})
        else:
            s = s.append(pd.read_csv(idxfile,dtype={'s_id':object}))
        
        #decreasing amount of computing
        #s = s[s['s_date']> '2016-04-01']
  
    print s.shape
    s = s.sort_values(['s_id','s_date'])
    s = s.reset_index()
    s = s[s.columns[1:]]
    
    resfile = resdir + os.sep + index.lower()
    globals()[index.lower()+'_chose'](resfile)

