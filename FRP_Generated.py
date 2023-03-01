# 生成论文里三个不需要风的FRP值：FRP within 500 km; Closest FRP; IDW FRP。
# FRP within 500 km需要你找到500km像素点内所有的FRP之和， Closest FRP需要你找到距离像素点最近的FRP的Fire Cluster的FRP之和，
# IDW FRP需要你找到反距离加权的500km内的FRP之和。
# 原文使用了500km，在此处我改为更小的更适合加里曼丹岛的200km FRP:0 frp;1 id; 2 area

from scipy.ndimage import morphology as mp
import numpy as np
import gdal
from glob import glob
import time as t
from math import *


def pix_region(row,col,circle):
    '''
    只需要定义它在501,582的图幅中的一点，然后就可以计算这一点中200km半径的所有点
    '''
    #b[100,100]=10
    temp = np.zeros([701,782])
    temp[row+100-100:row+100+101,col+100-100:col+100+101]=circle
    result= temp[100:-100,100:-100]
    return result

def pix_FRP_200km(FRP,row,col,circle):
    '''
    往像元输入一个值，500km以内的FRP之和
    '''
    region = pix_region(row,col,circle)
    output = np.where(region,FRP[0,:,:],0).sum()
    return output
def pix_Closest_IDW_FRP(FRP,row,col):
    '''
    往像元中输入一个值，这个值代表距离该像元最近的fire cluster的FRP之和,输出IDW_FRP
    '''

    def pix_IDW_FRP(FRP, distances):
        '''
        反向距离加权，权值函数使用一个线性的反距离函数 y=-(1/100)x+1,这里x取得是单位像元格子，不是km
        '''

        def linear_func(x):
            return -(1 / 100) * x + 1
        distances = np.array(distances)
        distances = np.where(distances < 100.0, distances, 100)  # 这是个ReLU，聪明的未来的我发现了吗
        output = 0
        # print(distances)
        for i in range(rows.shape[0]):
            output += FRP[0, rows[i], cols[i]] * linear_func(distances[i])
        return output
    points = np.where(FRP[0,:,:]>0)
    rows,cols = points[0],points[1]
    distances = []
    for j in range(rows.shape[0]):
        distances.append(sqrt((rows[j]-row)**2+(cols[j]-col)**2))
    min_distance = min(distances)
    position = distances.index(min_distance)
    ID = FRP[1,rows[position],cols[position]]
    closest = np.where(FRP[1,:,:]==ID,FRP[0,:,:],0).sum()
    IDW = pix_IDW_FRP(FRP,distances)
    return closest,IDW,min_distance,distances,rows,cols

def pix_WindWeighted_FRP(FRP,u850,v850,row,col,distances,rows,cols):
    '''
    这是那论文的精华（答辩）所在，风加权，根据风向和火烟方向的夹角算出权值，权值越大则越背离，权值乘以正常的距离就是加权距离，加权距离最小的火团的FRP以及加权距离会被返回
    distances,rows,cols接上个函数的用，免得重复计算浪费时间
    u表示经度方向上的风,v表示纬度方向上的风,u水平向东，v垂直向北。u为正,表示西风,从西边吹来的风。v为正,表示南风,从南边从来的风。
    '''
    Weighted_distances = distances
    if min(distances)==0: # 如果有0就不用找了
        min_Wdistance = min(Weighted_distances)
        Wposition = Weighted_distances.index(min_Wdistance)
        ID = FRP[1, rows[Wposition], cols[Wposition]]
        Wclosest = np.where(FRP[1, :, :] == ID, FRP[0, :, :], 0).sum()
        return Wclosest, min_Wdistance
    for i in range(rows.shape[0]):
        # 向量a是火到烟的向量，向量b是风的向量，两个的夹角用向量夹角公式算出cos
        a1 =col-cols[i]  #向量a的x轴
        a2 =-(row-rows[i]) #向量a的y轴，由于行号是从上往下的，所以加个负号
        b1 = u850[rows[i],cols[i]] # 经向
        b2 = v850[rows[i],cols[i]] # 纬向
        cos = (a1*b1+a2*b2)/(sqrt(a1**2+a2**2)*sqrt(b1**2+b2**2))
        angle = acos(cos)
        weight = angle/pi*5+1 # 根据论文里来的啊，除了把他那阶梯式的改为了线性的，让过度更加平滑之外，我都没变（其实人家也是线性连续，只是为了理解通顺而已）
        Weighted_distances[i] = distances[i]*weight

    min_Wdistance = min(Weighted_distances)
    Wposition = Weighted_distances.index(min_Wdistance)
    ID = FRP[1, rows[Wposition], cols[Wposition]]
    Wclosest = np.where(FRP[1, :, :] == ID, FRP[0, :, :], 0).sum()

    return Wclosest, min_Wdistance

g = gdal.Open(r'S:\all the data\FRP_TIFF\0823\0010.tif')
ary = g.ReadAsArray()
circle = np.load(r'E:\SmokeDetection\source\preprocess_code\round.npy') #一个半径是100个像素点的圆 shape=[201,201]，丢了的话可以拿np.where算距离后再搞一个
print(t.asctime())
# for i in range(ary.shape[1]):
# for j in range(ary.shape[2]):
row,col = 400,250
u850 = gdal.Open(r'S:\all the data\wind_processed\850hpa\0823\0010u.tif').ReadAsArray()
v850 = gdal.Open(r'S:\all the data\wind_processed\850hpa\0823\0010v.tif').ReadAsArray()
closest,IDW,min_dist,distances,rows,cols = pix_Closest_IDW_FRP(ary,row,col)
Wclosest, Wdistance = pix_WindWeighted_FRP(ary,u850,v850,row,col,distances,rows,cols)
FRPwithin500 = pix_FRP_200km(ary,row,col,circle)
print(closest,IDW,FRPwithin500,min_dist)
print(t.asctime())