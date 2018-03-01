# -*- coding: utf-8 -*-
"""
Created on Fri Mar 8 10:53:21 2017

@author: dxp
"""

import os, sys, logging, time, codecs

import urllib.request

colsName = ['s_name', 's_open', 's_last_close', 's_close',
            's_high', 's_low', 's_buy_1', 's_sell_1', 's_vol',
            's_turnover']

buyCols = [['s_buy%d_count' % i, 's_buy%d' % i] for i in range(1, 6)]
flattenBuyCols = [y for x in buyCols for y in x]
sellCols = [['s_sell%d_count' % i, 's_sell%d' % i] for i in range(1, 6)]
flattenSellCols = [y for x in sellCols for y in x]
colsName = colsName + flattenBuyCols + flattenSellCols + ['s_date']

useCols = ['s_id', 's_name', 's_date', 's_open', 's_high', \
           's_low', 's_close', 's_vol', 's_turnover']


def get_data(id, prefix):
    url = "http://hq.sinajs.cn/list=%s%s" % (prefix, id)
    data = urllib.request.urlopen(url).read().decode('cp936')
    data = data[data.find('"') + 1:data.rfind('"')].split(",")

    # data[1]对应s_open, 这里去除停牌
    if len(data) != 33 or float(data[1]) == 0.0:
        return []
    data_map = {}
    data_map['s_id'] = prefix + id
    for i in range(len(colsName)):
        data_map[colsName[i]] = data[i]

    #去掉名称中的空格
    data_map['s_name'] = data_map['s_name'].replace(' ', '')
    return [data_map[i] for i in useCols]


if __name__ == '__main__':
    basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    dir_list = ['log', 'data']
    mkdict = {}
    for i in dir_list:
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
                        filename=os.sep.join([mkdict['log'], 'sina.log']),
                        filemode='a')

    data_dir = sys.argv[1]
    dt = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    file_list = [i for i in os.listdir(data_dir) if \
                 os.path.isfile(data_dir + os.sep + i)]
    if len(file_list) < 1:
        logging.info("no data in %s" % data_dir)
        sys.exit(1)
    loadfile = os.sep.join([mkdict['data'], 'sina_%s' % dt])

    fw = codecs.open(loadfile, 'w', 'utf8')
    for i in file_list:
        prefix, id = i.split('.')[0].lower().split('#')
        url_data = get_data(id, prefix)
        # 去掉为空的数据
        if len(url_data) == 0:
            continue
        #print(url_data)
        fw.write('\t'.join(url_data)+'\n')
        logging.info("process file %s-%s" % (prefix, id))

    fw.close()







