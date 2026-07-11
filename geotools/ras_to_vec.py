from rasterio import features
from affine import Affine
from shapely import geometry
import rasterio as rio
import fiona
from pyproj import CRS
from shapely.geometry import shape
import os
from tqdm import tqdm
from glob import glob
from simplification.cutil import simplify_coords_vwp, simplify_coords

# IDENTITY = Affine.identity()
# GDAL_IDENTITY = IDENTITY.to_gdal()
def polygon_simplication(polygon, epsilon=30, method='vw'):
    exterior_coords = polygon.exterior.coords
    interior_coords = []
    for interior in polygon.interiors:
        interior_coords.append(interior.coords[:])

    exterior_coords = simplify_coords(exterior_coords, epsilon)
    new_interior_coords = []
    for interior in interior_coords:
        simplify_coords_temp = simplify_coords(interior, epsilon)
        if len(simplify_coords_temp) < 4:
            continue
        new_interior_coords.append(simplify_coords_temp)

    if len(exterior_coords) < 4:
        return None
    poly = geometry.Polygon(exterior_coords, new_interior_coords)

    return geometry.mapping(poly)


def polygonize(cls_map, mask, transform, connectivity=4, simplify=False, epsilon=30):
    shapes = features.shapes(cls_map, mask=mask, connectivity=connectivity, transform=transform)
    for s, v in shapes:
        if simplify:
            s = geometry.shape(s)
            s = polygon_simplication(s, epsilon=epsilon)
            if s is None:
                continue
        yield s, v


def ras2shp(ras_file, shp_file, classes, simplify=False):
    with rio.open(ras_file) as src:
        cls_map = src.read(1)
        # cls_map[cls_map == 100] = 0
        # cls_map[cls_map > 0] = 1  # 将非0值设为1
        # cls_map = np.where(cls_map == 3, 1, 0).astype('uint8') # 类别合并
        res = src.res[0]
        crs = src.crs.to_proj4() if src.crs else None
        transform = src.transform
        if crs is None:
            transform = Affine(transform.a, transform.b, -0.5, transform.d, -1, 0.5)

    schema = {'geometry': 'Polygon',
                'properties': {
                    'index': 'int',
                    'name': 'str',
                    'area': 'float'
                }
            }
    meta = {
        'driver': 'ESRI Shapefile',
        'crs': crs,
        'schema': schema,
        'encoding': 'utf-8'}
    k = 10e9 if res < 10e-4 else 1
    epsilon = res
    # epsilon = 10
    # print(epsilon)
    with fiona.open(shp_file, 'w', **meta) as dst:
        for poly, value in polygonize(
                cls_map,
                mask=cls_map != 0,
                transform=transform,
                simplify=simplify,
                epsilon=epsilon):
            if int(value) in classes:
                area0 = shape(poly).area*k
                feature = {
                    'geometry': poly,
                    'properties': {
                        'index': value,
                        'name': classes[int(value)],
                        'area': round(area0, 3)
                    }
                }

                dst.write(feature)
def main():
    # classes = {1: '1'}
    classes = {1: '1', 2: '2', 3: '3'}
    ras_path = r"D:\Data"
    out_path = r"D:\Data\shp"
    os.makedirs(out_path, exist_ok=True)
    ras_files = glob(ras_path + '/*.tif')
    for ras_file in tqdm(ras_files):
        name = os.path.splitext(os.path.basename(ras_file))[0]
        shp_file = os.path.join(out_path, name + '.shp')
        ras2shp(ras_file, shp_file, classes, True)

if __name__ == '__main__':
    main()