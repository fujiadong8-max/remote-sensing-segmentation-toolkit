from affine import Affine
import fiona
import rasterio
from rasterio import features
# from pyproj import CRS
import os
from tqdm import tqdm
from glob import glob
# import numpy as np

color_map = {
    1: (255, 0, 0),
    2: (0, 255, 0),
    3: (0, 0, 255),
    4: (255, 255, 0),
    5: (255, 0, 255),
    6: (0, 255, 255),
    7: (100, 255, 0),
    8: (0, 255, 100)
}
def rasterize(shpfile, tiffile, outfile, field_names, class_map, nodata=0):
    """Rasterize vector into a new raster.
    """
    with rasterio.open(tiffile) as ref:
        # img1 = ref.read(1)
        out_shape = ref.shape
        transform = ref.transform
        # crs = CRS(ref.crs).to_proj4() if ref.crs else None
        crs = ref.crs.to_proj4() if ref.crs else None
        if crs is None:
            transform = Affine(transform.a, transform.b, -0.5, transform.d, -1, 0.5)
    with fiona.open(shpfile) as src:
        shapes = []
        for i in src:
            for field_name in field_names:
                try:
                    class_type = i['properties'][field_name]
                    if class_type in class_map.keys() and i['geometry']:
                        geom = i['geometry']
                        shapes.append((geom, class_map[class_type]))
                except:
                    continue
    if not shapes:
        return
    meta = {
        'count': 1,
        'crs': crs,
        'width': out_shape[1],
        'height': out_shape[0],
        'transform': transform,
        'driver': 'GTiff',
        'dtype': rasterio.uint8,
        'nodata': nodata,
        'compress': 'lzw',
        'interleave': 'pixel',
    }
    image = features.rasterize(shapes,
                                out_shape=out_shape,
                                fill=0,
                                transform=transform)
    # 根据规则生成结果
    # image = np.where(image == 0, 0, np.where(img1 == 0, 1, img1))
    with rasterio.open(outfile, 'w', **meta) as dst:
        dst.write(image, indexes=1)
        dst.write_colormap(1, color_map)
        print('执行完成！')


if __name__ == '__main__':
    # class_map = {'河流、潮沟':1,'水库坑塘':2,'盐田、养殖池':3,'自然湿地':4，'农业用地':5，'建筑用地、油井'：6}
    class_map = {1:1, 2:2, 3:3, 4:4, 5:5, 6:6}
    shppath = r"C:\Users\1\Desktop\water seg\river data\shps"
    tifpath = r"C:\Users\1\Desktop\water seg\river data\images"
    outpath = os.path.join(os.path.dirname(shppath), 'masks')
    # maskpath = os.path.join(shppath, 'mask')
    os.makedirs(outpath, exist_ok=True)
    shpfiles = sorted(glob(shppath + '/*.shp'))
    for shpfile in tqdm(shpfiles):
        name = os.path.splitext(os.path.basename(shpfile))[0]
        tiffile = os.path.join(tifpath, name + '.tif')
        outfile = os.path.join(outpath, name + '.tif')
        field_names = ['Class6']
        rasterize(shpfile, tiffile, outfile, field_names, class_map)

