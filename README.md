# Predicting-Minimum-Smoke-Height
2018年RSE上，有一个拿随机森林加上一大堆大气和地理数据做烟高检测的文章，我复现它的数据处理和模型代码，Python3.7,gdal,numpy,netCDF4,glob,tqdm(可不要)随便配版本，都能跑。
CALIOP处理的代码我用3.8的，pyhdf这个包很难下，建议下whl文件自己手动
论文链接：https://doi.org/10.1016/j.rse.2017.12.027.
个人评价这篇论文：从重要性对比来看，作者想做的效果没做起来，效果马马虎虎，由于发的早，数据用的多，上了RSE。中规中矩的文章，效果估计不会太差，很适合做数据对比。
改动细节：作者判定500km以内有火的即为被影响区域，这个区域的判定我没有找到依据，为了适应加里曼丹岛的尺度，改为了200km半径，其它的没改。
