# 这是一个把FRP L2数据（csv格式转换成TIFF格式的代码），葵花左上右下坐标(107.36, 5.48)，(119.0, -4.54)，shape=[501,582]
import csv
import gdal
import glob
import numpy as np
import csv
import os

def mk_pic(data, fn):
    '''
    制作数据，data就是分配进来的数据，date是日期，time是时间，direction是方向
    '''
    temp_img = gdal.Open(r'S:\all the data\new_new_data\0816\0000.tif')  # 找个范例，这样好搞
    temp_geotfm, temp_geoprj = temp_img.GetGeoTransform(), temp_img.GetProjection()
    driver = gdal.GetDriverByName('GTiff')
    output = driver.Create(fn, 582, 501, 3, gdal.GDT_Float32)
    for i in range(1,4):
        output.GetRasterBand(i).WriteArray(data[i-1,:,:])
    output.SetGeoTransform(temp_geotfm)
    output.SetProjection(temp_geoprj)
    del output
    print('出完一张图：' + r'{}\{}.tif'.format(date, time))

img = gdal.Open(r'S:\all the data\new_new_data\0822\0010.tif') #找个副本
ary = img.ReadAsArray()
geotfm = img.GetGeoTransform()
geoprj = img.GetProjection()

new_ary = np.zeros((3,ary.shape[1],ary.shape[2])) # 第一个通道记录FRP(Wm^-2)，第二个记录Hot(ID)，第三个通道记录Area(km^2)
def transform(date,time):
    output_ary = np.copy(new_ary)
    with open(r'S:\all the data\FRP_Processed\{}\H08_2015{}_{}_L2WLF010_FLDK.06001_06001.csv'.format(date,date,time),'r',encoding='GBK',newline='') as f:
        dd= csv.reader(f)
        for i,d in enumerate(dd): #['# ID', 'Year', 'Month', 'Day', 'Time(UTC)', 'Lat', 'Lon', 'Area(km^2)', 'Volcano', 'Level', 'Reliability', 'FRP(Wm^-2)', 'QF', 'Hot(ID)']
            if i>=2:
                if -4.54<eval(d[5])<=5.48 and 107.36<=eval(d[6])<119.0 and d[-2]!='2':
                    row, col = int((5.48-eval(d[5]))/0.02), int((eval(d[6])-107.36.0)/0.02)
                    output_ary[0,row,col]=eval(d[-3])
                    output_ary[1,row,col]=eval(d[-1])
                    output_ary[2,row,col]=eval(d[-7])

    fn = r'S:\all the data\FRP_TIFF\{}\{}.tif'.format(date,time)
    mk_pic(output_ary,fn)


fns = glob.glob(r'S:\all the data\FRP_Processed\*\*.csv')
for f in fns:
    date = f.split('\\')[-2]
    time = f.split('_')[3]
    transform(date,time)
