# coding:utf-8
import os
from osgeo import gdal
from glob import glob
from tqdm import tqdm
import rasterio
from rasterio.mask import mask
import geopandas as gpd

def extract_by_shp(in_shp_path, input_raster_path, output_raster_path):
    if not os.path.exists(input_raster_path):
        print("输入栅格文件不存在")
        return
    if not os.path.exists(in_shp_path):
        print("输入矢量文件不存在")
        return
    input_raster = gdal.Open(input_raster_path)
    if input_raster is None:
        print("无法打开输入栅格文件")
        return
    # 使用gdal.Warp进行裁剪
    result = gdal.Warp(
        output_raster_path,  # 输出文件路径
        input_raster_path,        # 输入栅格数据集
        cutlineDSName=in_shp_path,  # 裁剪使用的矢量边界文件路径
        format='GTiff',      # 输出格式
        cropToCutline=True,  # 是否按照矢量边界输出
        creationOptions=[            # 添加压缩参数
        'COMPRESS=LZW',          # 使用 LZW 无损压缩
        'TILED=YES',             # 启用分块存储（提升大文件读写效率）
        'PREDICTOR=2'            # 对连续色调数据（如 DEM）使用预测器优化压缩
    ],
        # dstNodata=0          # 设置输出无效值为0
    )
    
    # 清理
    del result

if __name__ == "__main__":
    shp_file = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\shps"  # 替换为你的shapefile路径
    ras_file = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\Sentinel2_Median_2024.tif"  # 替换为你的输入影像路径
    out_file = r"C:\Users\1\Desktop\遥感地物提取\test data 2024\images"  # 替换为你希望保存的裁剪后影像路径
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    extract_by_shp(shp_file, ras_file, out_file)

