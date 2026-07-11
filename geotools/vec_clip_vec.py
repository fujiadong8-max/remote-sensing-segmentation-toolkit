# -*- coding: utf-8 -*-
import geopandas as gpd
import os

def shp_clip(shp_file, out_file, clip_file):
    gdf_clip = gpd.read_file(clip_file, encoding='gbk')
    gdf_src = gpd.read_file(shp_file, encoding='gbk')
    gdf_src_transformed = gdf_src.to_crs(gdf_clip.crs)
    result = gpd.overlay(gdf_src_transformed, gdf_clip, how="intersection")
    result.to_file(out_file, encoding='gbk')

if __name__ == "__main__":
    clip_file = r"D:\Data\test\test13矢量裁剪矢量\clip\baoquanling_clip.shp"
    shp_file = r"D:\Data\test\test13矢量裁剪矢量\src\baoquanling_clip.shp"
    out_file = r"D:\Data\test\test13矢量裁剪矢量\baoquanling_clip.shp"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    shp_clip(shp_file, out_file, clip_file)

