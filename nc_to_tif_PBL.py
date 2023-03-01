# 把ERA5的PBL数据分成每个日期一个文件夹（如0825），然后再在文件夹中分UTC时刻（如0100.tif)
from glob import glob
import netCDF4 as nc
import numpy as np
import os
import gdal
import cv2

def assign_data(data_pth, month):
    '''
    data指的是输入的nc文件；month指的是这个文件代表的月份。
    目前这个代码仅用于毕业，所以默认设定文件只有netCDF4的PBL
    每个日期有9个时刻的数据0000-0800整点数据，需要把它们输出成TIF，命名法：月\时刻PBL，举例0830\0030.tif
    至于怎么分给每个10分钟一景的影像，在写这个代码的时候我不知道。就这样 ————20230222 15:30 宿舍
    '''
    def allocate(whole, month):
        '''
        把所有的数据分配date和time
        '''

        def change_size(data):
            '''
            cv2的resize,默认双线性插值
            '''
            temp = data[:-1,:-1] #当左上为计数点的时候，需要减去一条边才好算，不然那个经纬度都得加一个像元单位
            if not temp.shape==(44,52): print(ValueError('风的shape值有问题,当前shape值为{}'.format(temp.shape))) #如果是地面风，它的shape应该是[101,130]
            resized = cv2.resize(temp,(650,550)) #经过计算，需要插成这样才能对的上葵花的分辨率，默认双线性 注意了！！这个resize的第二个参数是(宽，高)
            output = resized[26:-23,18:-50] #pbl就这么算的，葵花左上右下坐标(107.36, 5.48)，(119.0, -4.54)
            if not output.shape==(501,582): print(ValueError('不知道哪里出问题了，你输出的shape错了，当前shape为{}'.format(output.shape)))
            return output

        def mk_pic(data, date, time):
            '''
            制作数据，data就是分配进来的数据，date是日期，time是时间，direction是方向
            '''
            temp_img = gdal.Open(r'S:\all the data\new_new_data\0816\0000.tif') #找个范例，这样好搞
            temp_geotfm,temp_geoprj = temp_img.GetGeoTransform(),temp_img.GetProjection()
            temp_ary = temp_img.ReadAsArray()
            temp_shape = temp_ary.shape
            driver = gdal.GetDriverByName('GTiff')
            output = driver.Create(r'{}\{}.tif'.format(date,time),582,501,1,gdal.GDT_Float32)
            output.GetRasterBand(1).WriteArray(data)
            output.SetGeoTransform(temp_geotfm)
            output.SetProjection(temp_geoprj)
            del output
            print('出完一张图：'+r'{}\{}.tif'.format(date,time))

        if month == 8 or month=='8':
            dates = ['0816','0817','0818','0819','0820','0821','0822','0823','0824','0825','0826','0827','0828','0829','0830', '0831']
        elif month == 9 or month=='9':
            dates = ['0901','0902','0903','0904','0905','0906','0907','0908','0909','0910','0911','0912','0913','0914','0915']
        else: return ValueError('月份错了')

        for i,date in enumerate(dates):
            temp = whole[i:i+9]
            '''if kind ==250 or kind =='250' or kind=='250hpa':
                            u_temp = u_temp[0]
                            v_temp = v_temp[0]
                        if kind == 500 or kind == '500' or kind == '500hpa':
                            u_temp = u_temp[1]
                            v_temp = v_temp[1]
                        if kind == 850 or kind == '850' or kind == '850hpa':
                            u_temp = u_temp[2]
                            v_temp = v_temp[2]'''
            for t in range(9):
                result_ary = change_size(temp[t])

                time = '0{}00'.format(t)
                mk_pic(result_ary, date, time)

    data = nc.Dataset(data_pth)
    whole = np.array(data.variables['blh'])
    os.chdir(r'S:\all the data\PBL_Processed')
    # print(u_whole.shape,v_whole.shape)
    allocate(whole,month)

if __name__ =='__main__':
    pth = r'S:\all the data\PBL\AUG\adaptor.mars.internal-1676967408.6380289-31408-6-c43d6f61-f275-4fb5-86a3-8d207ce7d620.nc'
    assign_data(pth,9)
