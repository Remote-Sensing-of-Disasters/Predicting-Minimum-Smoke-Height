# 把每小时的风数据扩充到十分钟一景
import os
from glob import glob
import time as t
import shutil
fns_dic = glob(r'S:\all the data\wind_processed\*')
for fn_dic in fns_dic:
    os.chdir(fn_dic)
    fns = glob(r'{}\*\*.tif'.format(fn_dic))
    for fn in fns:
        date = fn.split('\\')[-2]
        time = fn.split('\\')[-1][:-5]
        dirt = fn.split('\\')[-1][-5]
        hour = eval(time[1])
        if hour == 0:
            for i in range(1,3,1):# i= 1,2
                name = r'{}\0{}{}0{}.tif'.format(date,hour,i,dirt)
                print(name)
                shutil.copy(fn,name)
        if 1<=hour<=7:
            for i in range(1,3,1):# i= 1,2
                name = r'{}\0{}{}0{}.tif'.format(date,hour,i,dirt)
                shutil.copy(fn,name)
            for j in range(3,6,1):
                name = r'{}\0{}{}0{}.tif'.format(date, hour-1, j, dirt)
                shutil.copy(fn, name)
        if hour==8:
            for j in range(3,6,1):
                name = r'{}\0{}{}0{}.tif'.format(date, hour-1, j, dirt)
                shutil.copy(fn, name)
