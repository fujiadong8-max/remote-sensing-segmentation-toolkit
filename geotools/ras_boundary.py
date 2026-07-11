import fiona
import rasterio as rio
from rasterio import features
from glob import glob
import os
from tqdm import tqdm
# from pyproj import CRS
from pathlib import Path
import numpy as np

def ras_bound(ras_file, shp_file):
    with rio.open(ras_file) as src:
        crs = src.crs.to_proj4()  # 读取坐标信息
        # transform = src.transform  # 读取仿射矩阵
        # meta = src.meta
        mask1 = src.read(1)
        mask1[mask1 != 0] = 255
        mask2 = features.sieve(mask1, size=800)
        
        # mask3 = (mask1 != src.nodata) & (mask1 > 0)
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



if __name__ == "__main__":
    ras_path = r"D:\Data\1_clip2"
    bound_path = os.path.join(ras_path, 'boundary1')
    os.makedirs(bound_path, exist_ok=True)
    ras_files = glob(ras_path + '/GF06*.tif')
    for ras_file in tqdm(ras_files):
        shp_file = os.path.join(bound_path, (Path(ras_file).stem + '.shp'))
        ras_bound(ras_file, shp_file)
