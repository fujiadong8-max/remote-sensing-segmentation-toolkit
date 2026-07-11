import os
import fiona
import rasterio as rio
from rasterio import features
from pyproj import CRS
from osgeo import gdal
import geopandas as gpd

def ras_bound(ras_file, shp_file):
    with rio.open(ras_file) as src:
        crs = CRS(src.crs).to_proj4()  # 读取坐标信息
        # transform = src.transform  # 读取仿射矩阵
        # meta = src.meta
        mask1 = src.read_masks(1)
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



def shp_clip(shp_file, out_file, clip_file):
    gdf_clip = gpd.read_file(clip_file)
    gdf_src = gpd.read_file(shp_file)
    result = gpd.overlay(gdf_src, gdf_clip, how="intersection")
    result.to_file(out_file, encoding='utf-8')


def ras_clip_ras(ras_file, clip_file, vec_file, out_file):
    ras_bound(ras_file, clip_file)
    shp_clip(vec_file, out_file, clip_file)


if __name__ == "__main__":
    ras_file = r"D:\Data\test\test14栅格裁剪矢量\mask\光伏5.tif"
    vec_file = r"D:\Data\test\test14栅格裁剪矢量\shps\光伏5.shp"
    out_path = r"D:\Data\test\test14栅格裁剪矢量\output111"
    os.makedirs(out_path, exist_ok=True)
    name = os.path.basename(vec_file)
    out_file = os.path.join(out_path, name)
    clip_file = os.path.join(out_path, 'clip_temp.shp')
    ras_clip_ras(ras_file, clip_file, vec_file, out_file)