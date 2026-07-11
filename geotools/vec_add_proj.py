import os
from glob import glob
from tqdm import tqdm
import geopandas as gpd

def proj_add(src_file, dst_file):
    gdf = gpd.read_file(src_file)

    if gdf.crs is None:
        gdf = gdf.set_crs('EPSG:4326', allow_override=True)  # 添加地理坐标系信息
        gdf = gdf.to_crs("EPSG:3857")  # 转换为投影坐标系
    else:
        gdf = gdf.to_crs("EPSG:4326") # 转换为地理坐标系
        gdf = gdf.to_crs("EPSG:3857") # 转换为投影坐标系

    gdf.to_file(dst_file, driver='ESRI Shapefile')

def remove_crs(src_file, dst_file):
    gdf = gpd.read_file(src_file)
    gdf_no_crs = gdf.set_crs(None, allow_override=True)
    gdf_no_crs.to_file(dst_file)


if __name__ == "__main__":
    src_path = r"D:\Data\test\test15矢量添加地理信息\shp_crs_no"
    dst_path = r"D:\Data\test\test15矢量添加地理信息\shp_crs_add111"
    os.makedirs(dst_path, exist_ok=True)
    src_files = glob(src_path + '/*.shp')
    for src_file in tqdm(src_files):
        dst_file = os.path.join(dst_path, os.path.basename(src_file))
        proj_add(src_file, dst_file)
        # remove_crs(src_file, dst_file)
