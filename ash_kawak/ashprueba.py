#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import numpy as np
from scipy.signal import convolve2d
from osgeo import gdal,osr
from netCDF4 import Dataset


datadir = "/var/tmp/ash/input/"
outdir = "/var/tmp/ash/output/"
geotransform = None
projection = None


def get_file(files, band):
    for file in files:
        if band in file:
            return file
    print("No existe la banda ", band)
    exit(1)
    return 'Error'

def get_projection(nc, nx, ny):
    global geotransform
    global projection
    H = nc.variables['goes_imager_projection'].perspective_point_height
    lat_or = nc.variables['goes_imager_projection'].latitude_of_projection_origin
    lon_or = nc.variables['goes_imager_projection'].longitude_of_projection_origin
    xmin = nc.variables['x_image_bounds'][0] * H
    xmax = nc.variables['x_image_bounds'][1] * H
    ymin = nc.variables['y_image_bounds'][1] * H
    ymax = nc.variables['y_image_bounds'][0] * H
    xres = (xmax - xmin) / float(ny)
    yres = (ymax - ymin) / float(nx)
    geotransform = (xmin, xres, 0, ymax, 0, -yres)
    srs = osr.SpatialReference()            # Establece el ensamble
    srs.ImportFromProj4("+proj=geos +h={} +ellps=GRS80 +lat_0={} +lon_0={} +sweep=x +no_defs".format(H, lat_or, lon_or))
    projection = srs.ExportToWkt()
    #print("Geotransform ", geotransform, " Projection ", projection)

    
def leeNC(path):
    global projection
    print('Path ', path)
    r = re.search('CG_ABI-L2-([A-Z]{3})', path)
    variable = r.groups(0)[0]
    nc = Dataset(path, 'r')
    data = nc.variables[variable][:].data
    if not projection:
        nx = data.shape[0]
        ny = data.shape[1]
        get_projection(nc, nx, ny)
        #get_projection(path)
    return data


def array2raster(newRasterfilename, array):
    global geotransform
    global projection
    print('Guardando ', newRasterfilename)
    cols = array.shape[1]
    rows = array.shape[0]
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfilename, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetProjection(projection)
    outRaster.SetGeoTransform(geotransform)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    #outRasterSRS = osr.SpatialReference()
    #outRasterSRS.ImportFromEPSG(4326)
    #outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

    
def main():
    if len(sys.argv) < 2:
        print("Usanza: ", sys.argv[0], " <sYYYYjjjhhmm>")
        exit(1)
	
    # find_files
    sdate_id = sys.argv[1]
    files = glob.glob(datadir+'*'+sdate_id+'*.nc')
    pathC11 = get_file(files, 'C11')
    pathC13 = get_file(files, 'C13')
    pathC14 = get_file(files, 'C14')
    pathC15 = get_file(files, 'C15')
    #    pathLST = get_file(files, 'LST')

    b11 = leeNC(pathC11)
    b13 = leeNC(pathC13)
    b14 = leeNC(pathC14)
    b15 = leeNC(pathC15)

    a = np.subtract(b13, b15)
    b = np.subtract(b14, b15)

    a = np.where(a <= 0, 1.0, 0.0)
    b = np.where(b <= 0, 1.0, 0.0)
    c = np.where((a == 1) & (b == 1), 1.0, 0.0)
    d = np.subtract(b13, b11)
    d = np.where(d <= 0.5, 1.0, 0.0)
    e = np.where((c == 1) & (d == 1), 1.0, 0.0)

    #blst = np.where((blst > 273.15) & (blst < 283.15), 0.0, blst)

    #sat.sensor.prod-YYYY.MMDD.HHmm
    array2raster(outdir+"goes16.abi.ASH-"+sdate_id+'.tif', e)
    array2raster(outdir+"goes16.abi.13_15-"+sdate_id+'.tif', a)
    array2raster(outdir+"goes16.abi.14_15-"+sdate_id+'.tif', b)
    array2raster(outdir+"goes16.abi.C-"+sdate_id+'.tif', c)
    array2raster(outdir+"goes16.abi.D-"+sdate_id+'.tif', d)

if __name__ == "__main__":
    main()

