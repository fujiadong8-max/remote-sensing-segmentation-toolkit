import os
import fiona
import rasterio as rio
from rasterio import features
from pyproj import CRS
from osgeo import gdal

def ras_bound(ras_file, shp_file):
    with rio.open(ras_file) as src:
        crs = CRS(src.crs).to_proj4()  # 读取坐标信息
        # transform = src.transform  # 读取仿射矩阵
        # meta = src.meta
        mask1 = src.read_masks(1)
        mask1[mask1 != 0] = 255
        mask2 = features.sieve(mask1, size=800)
        mask = mask2 == 255
        shapes = features.shapes(mask2, mask=mask, transform=src.transform)
        schema = {'geometry': 'Polygon',
                  'properties': {'class_id': 'float'}}
        with fiona.open(shp_file, mode='w', driver='ESRI Shapefile',schema=schema,crs=crs, encoding='utf-8') as layer:
            for poly,value in shapes:
                feature = {
                    'geometry': poly,
                    'properties': {
                        'class_id': value,
                    }
                }
                layer.write(feature)

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
        # dstNodata=0          # 设置输出无效值为0
    )
    
    # 清理
    del result

def ras_clip_ras(clip_file, shp_file, ras_file, out_file):
    ras_bound(clip_file, shp_file)
    extract_by_shp(shp_file, ras_file, out_file)


if __name__ == "__main__":
    ras_file = r"D:\Data\依兰县分类整理\各家测试情况\商汤\10米大豆\image1\yilan_0804.tif"
    clip_file = r"D:\Data\依兰县分类整理\各家测试情况\商汤\10米大豆\image1\yilan_0423_clip2.tif"
    out_path = r"D:\Data\依兰县分类整理\各家测试情况\商汤\10米大豆\image1\yilan_0804_clip2.tif"
    os.makedirs(out_path, exist_ok=True)
    name = os.path.basename(ras_file)
    out_file = os.path.join(out_path, name)
    shp_file = os.path.join(out_path, 'clip.shp')
    ras_clip_ras(clip_file, shp_file, ras_file, out_file)