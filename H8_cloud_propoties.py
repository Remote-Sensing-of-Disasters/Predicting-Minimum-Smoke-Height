#葵花8的云数据插值并裁剪成和输入的葵花图像一样的图片，tif格式
import netCDF4 as nc
import glob
import numpy as np
import gdal
from tqdm import tqdm
import os
import cv2
def clip(cloud_pth,origin_pth,result_pth):
    '''
    输入H8的云图的路径，以及tif格式的H8的图，带geotransform的，输出一个相同shape的结果图，只有一个波段“cloud type"
    '''
    data = nc.Dataset(cloud_pth)
    # print(data.variables)
    # d =nc.Dataset(r'F:\Himawari-8\0826\NC_H08_20150826_0330_R21_FLDK.06001_06001.nc')

    cltype = np.array(data.variables['CLTYPE'])
    cltype = np.where(cltype == 0, 0, 1)
    # num = np.where(cltype==0,1,0)
    # print(cltype.shape[0]*cltype.shape[1])
    # print(num.sum())
    latitude = np.array(data.variables['latitude'])  # 纬度
    longitude = np.array(data.variables['longitude'])  # 经度
    latitude = [round(latitude[i], 2) for i in range(latitude.shape[0])]
    longitude = [round(longitude[i], 2) for i in range(longitude.shape[0])]
    root_data = gdal.Open(origin_pth)  # geotransform(107.36, 0.02, 0.0, 5.48, 0.0, -0.02)
    geotrm = root_data.GetGeoTransform()
    root_ary = root_data.ReadAsArray()
    shape = root_ary.shape
    upleft_idx, downright_idx = (1368, 2726), (1950, 3227)
    cltype_nearest = cv2.resize(cltype,(6001,6001),interpolation=cv2.INTER_NEAREST)
    result_ary = cltype_nearest[upleft_idx[1]:downright_idx[1],upleft_idx[0]:downright_idx[0]]
    '''for row in tqdm(range(shape[1]),desc='single process:{}'.format(origin_pth[-13:])):
        for col in range(shape[2]):
            r, c = 1088, 540
            lat, lon = geotrm[3] + geotrm[5] * row, geotrm[0] + geotrm[1] * col
            while not (latitude[r] >= lat >= latitude[r + 1]):
                r += 1
            while not longitude[c] <= lon <= longitude[c + 1]:
                c += 1
            result_ary[row, col] = cltype[r, c]
            if lat == 5.50:
                print(r)'''
    drive = gdal.GetDriverByName('GTiff')
    out = drive.Create(result_pth, shape[2], shape[1], 1, gdal.GDT_Int16)
    out.GetRasterBand(1).WriteArray(result_ary)
    out.SetGeoTransform(geotrm)
    out.SetProjection(root_data.GetProjection())
    del out



dates = glob.glob(r'S:\all the data\new_new_data\*')
dates = [d[-4:] for d in dates]
fns = []
for d in dates:
    fns+=glob.glob(r'S:\all the data\new_new_data\{}\*.tif'.format(d))
for fn in fns:
    date = fn.split('\\')[-2]
    time = fn.split('\\')[-1][:-4]
    if len(glob.glob(r'S:\all the data\H8_Cloud\{}\*_{}_*'.format(date,time)))==0:
        print('有葵花数据却少了云数据，日期：{}；时间：{}'.format(date,time))
        continue
    cloud_pth = glob.glob(r'S:\all the data\H8_Cloud\{}\*_{}_*'.format(date,time))[0]
    origin_pth = fn
    if not os.path.exists(r'S:\all the data\H8_Cloud_TIF\{}'.format(date)): os.mkdir(r'S:\all the data\H8_Cloud_TIF\{}'.format(date))
    result_pth = r'S:\all the data\H8_Cloud_TIF\{}\{}.tif'.format(date,time)
    if os.path.exists(result_pth):
        continue
    if not os.path.exists(cloud_pth):
        FutureWarning('记得以后加个:{}_{}'.format(date,time))
        continue
    print('准备跑{}_{}'.format(date, time))
    clip(cloud_pth,origin_pth,result_pth)
    print('跑完了{}_{}'.format(date, time))

