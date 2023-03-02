# 遍历所有区域内的CALIOP数据，看看是否符合要求，符合就返回值time,row,col

from osgeo import gdal
from glob import glob
import os
import numpy as np
from pyhdf.SD import SD
circle = np.load(r'S:\all the data\round.npy')


def pix_region(row,col,circle):
    '''
    只需要定义它在501,582的图幅中的一点，然后就可以计算这一点中200km半径的所有点
    '''
    #b[100,100]=10
    temp = np.zeros([701,782])
    temp[row+100-100:row+100+101,col+100-100:col+100+101]=circle
    result= temp[100:-100,100:-100]
    return result
def input_CALIOP(fn):
    # 输入一个CALIOP的文件hdf，输出这个文件中被认为是烟的行列号和时间
    # 遍历CALIOP像素经纬度并对应上具体的葵花行列号
    hdf = SD(fn)
    lon = hdf.select('Longitude')[:]
    lat = hdf.select('Latitude')[:]
    VFM = hdf.select('Feature_Classification_Flags')[:]
    utc = hdf.select('Profile_UTC_Time')[:]
    positions=[] #[[row,col]]
    times = [] #shape=(7,)
    if not len(lon)==len(lat):raise ValueError('Wrong Length from Lon or Lat!!!')
    for i in range(len(lon)):    
        if 107.36<=lon[i]<119.0 and -4.54<lat[i]<=5.48:
            for v10 in VFM[i][:]:
                v2=bin(v10)
                if len(v2)>=15:
                    if v2[-13]=='1': # 官方说二进制第13位是气溶胶的QA，论文里也用这个的
                        if ((v2[-3:] == '011'and (v2[-12:-9]=='110'or v2[-12:-9]=='011'))or(v2[-3:] == '100'and v2[-12:-9]=='100')): 
                            # 判定是否有这三种烟（平流层一种对流层两种）
                            col = int((lon[i]-107.36)/0.02) # 除非你想算算命，否则别用整除//
                            row = int((5.48-lat[i])/0.02)
                            positions.append([row,col])
                            time = []
                            hour_time=(utc[i]-int(utc[i]))*24 # 转换成小时以及小数点
                            min10_hour = 1/6 #以它的计算方式算出10分钟在一小时的度量中应该是多少值
                            for j in range(-3,4,1): #开始扩展时间了,左右30分钟，共7张图
                                true_time = hour_time+j*min10_hour
                                hour='0{}'.format(int(true_time))
                                min10 = '{}0'.format(int((true_time-int(true_time))*6)) 
                                time.append(hour+min10)
                            times.append(time)
                            break
    return positions,times

# 调用对应的火数据判定范围
def check(row,col,date,time):
    '''
    单独搜索一个时刻，该区域是否有火。
    它得调用那个圆形文件round.npy在那FRP图里搜索
    '''
    os.chdir(r'S:\all the data\FRP_TIFF')
    ary = gdal.Open(r'{}\{}.tif'.format(date,time)).ReadAsArray()
    region=pix_region(row,col,circle)
    frp_sum = np.where(region,ary[0,:,:],0).sum()
    #print(np.where(ary[0]),frp_sum)
    if frp_sum>0:
        return 1
    else:
        return 0



# 输出对应的行列号编码以及时间编码，暂定时刻编码前后各三十分钟，七张图
fn = r'S:\all the data\CALIOP\CAL_LID_L2_VFM-Standard-V4-20.2015-08-30T05-57-49ZD.hdf'
date = fn.split('2015-')[-1][:2]+fn.split('2015-')[-1][3:5]
print(date)
positions,times = input_CALIOP(fn)
if len(positions)!= len(times):
       raise ValueError('pos_length:{},time_length:{}'.format(len(positions),len(times)))

for i in range(len(positions)):
    [row,col] = positions[i]
    for t in times[i][:]:
        if not check(row,col,date,t):
            times[i].remove(t)
    if len(times[i])==0:
        positions.remove([row,col])
        times.remove([])



