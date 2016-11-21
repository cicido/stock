#!/usr/bin/env python
# *-* coding:utf8 *-*
'''
Created on 2015年11月13日

@author: dxp
'''
import sys, codecs, logging, os, time
import dbhandle, shutil

tablename = "stock_k_days"
columnlist = ['s_id', 's_name', 's_date', 's_open', 's_high', \
                  's_low', 's_close', 's_vol', 's_turnover']
columnlen = len(columnlist)
# datadir = r"D:\stock"
  
def load_k_data(filename,sdate,edate):  
    fr = codecs.open(filename, 'r', 'cp936')
    line = fr.readline().strip().split()
    s_id = line[0]
    s_name = ''.join(line[1:-2])
    for line in fr.readlines()[1:]:
        line = line.strip().split('\t')
        # no s_id,s_name
        if len(line) != columnlen - 2 or float(line[-2]) == 0:  
            continue
        line[0] = '-'.join(line[0].split('/'))
        if line[0] < sdate or line[0] > edate:
            continue
        if float(line[-1]) == 0:
            continue
        fw.write("%s\t%s\t%s\n" % (s_id, s_name, '\t'.join(line)))
    fr.close()
    logging.info("process file %s" % filename)
    
# from file collection to put all date into one file
if __name__ == '__main__':
    basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    relmklist = ['log','data']
    mkdict = {}
    for i in relmklist:
        mkdict[i] = basedir + os.sep + i
        
    for i in mkdict.values():
        if not os.path.exists(i):
            try:
                os.mkdir(i)
            except:
                print "mkdir %s failed,exit..." % i
                sys.exit(1)
            
    logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            filename=os.sep.join([mkdict['log'] , 'load.log']),
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
        load_k_data(datadir + os.sep + i,sdate, edate)
        #shutil.move(datadir + os.sep + i, mkdict['backdata'] + os.sep + curhour + i)
        #os.remove(datadir + os.sep + i)
    fw.close()

    curs = dbhandle.mysql_handble().getcursor()
    sql = "load data local infile '" + loadfile + \
    "' into table " + tablename + \
    " fields terminated by '\\t'" + \
    " lines terminated by '\\n'"
    print sql
    #curs.execute(sql)
