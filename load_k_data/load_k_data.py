#!/usr/bin/env python
# *-* coding:utf8 *-*
'''
Created on 2015年11月13日

@author: dxp
load_k_data.py 数据预处理模块，处理成pandas
可以直接加载的文件数据
'''
import sys, codecs, logging, os

table_name = "stock_k_days"
column_list = ['s_id', 's_name', 's_date', 's_open', 's_high', \
                  's_low', 's_close', 's_vol', 's_turnover']
column_len = len(column_list)
# datadir = r"D:\stock"


def load_k_data(filename, sdate, edate):
    fr = codecs.open(filename, 'r', 'cp936')
    line = fr.readline().strip().split()
    s_id = filename.split(os.sep)[-1].split('.')[0].replace('#', '').lower()
    s_name = ''.join(line[1:-2])
    for line in fr.readlines()[1:]:
        line = line.strip().split('\t')
        # no s_id,s_name
        if len(line) != column_len - 2 or float(line[-2]) == 0:
            continue
        line[0] = '-'.join(line[0].split('/'))
        if line[0] < sdate or line[0] > edate:
            continue
        if float(line[-1]) == 0:
            continue
        fw.write("%s\t%s\t%s\n" % (s_id, s_name, '\t'.join(line)))
    fr.close()

    
# from file collection to put all date into one file
if __name__ == '__main__':
    basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    relmklist = ['log', 'data']
    mkdict = {}
    for i in relmklist:
        mkdict[i] = basedir + os.sep + i
        
    for i in mkdict.values():
        if not os.path.exists(i):
            try:
                os.mkdir(i)
            except:
                print("mkdir %s failed,exit..." % i)
                sys.exit(1)
            
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=os.sep.join([mkdict['log'], 'load.log']),
            filemode='a')
    
    datadir = sys.argv[1]            
    sdate = sys.argv[2]
    edate = sys.argv[3]
    relfilelist = [i for i in os.listdir(datadir) if \
                   os.path.isfile(datadir + os.sep + i)]
    if len(relfilelist) < 1:
        logging.info("no data in %s" % datadir)
        sys.exit(1) 
    loadfile = os.sep.join([mkdict['data'], 'loaddata_%s_%s' %(sdate,edate)])
    
    fw = codecs.open(loadfile, 'w', 'utf8')
    for i in relfilelist:
        abs_file = datadir + os.sep + i
        load_k_data(abs_file, sdate, edate)
        logging.info("process file %s" %abs_file)
        # shutil.move(datadir + os.sep + i, mkdict['backdata'] + os.sep + curhour + i)
        # os.remove(datadir + os.sep + i)
    fw.close()