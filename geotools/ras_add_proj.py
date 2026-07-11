# -*- coding: utf-8 -*-
import rasterio as rio


def proj_add_rio(src_file, proj_file, dst_file):
    with rio.open(proj_file) as like:
        profile = like.profile
        
    with rio.open(src_file) as src:
        data = src.read()
        width = src.width
        height = src.height

    profile.update(count = 3, width=width, height=height)
    with rio.open(dst_file, 'w', **profile) as dst:
        dst.write(data)

if __name__ == "__main__":
    src_file = r"D:\Data\test\test11栅格添加地理信息\001.png"
    prj_file = r'D:\Data\test\test11栅格添加地理信息\002.tif'  
    dst_file = r"D:\Data\test\test11栅格添加地理信息\0011.tif"
    proj_add_rio(src_file, prj_file, dst_file)

