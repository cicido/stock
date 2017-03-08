# -*- coding: utf-8 -*-
"""
Created on Fri Mar 8 10:53:21 2017

@author: dxp
"""

import os,sys

import urllib2

if __name__ == '__main__':
    #code = sys.argv[1]
    response = urllib2.urlopen("http://hq.sinajs.cn/list=sz300232")
    print response.read().decode('cp936')


