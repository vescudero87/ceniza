#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import glob
import numpy as np
from osgeo import gdal, osr
from netCDF4 import Dataset


# Variables globales
datadir = "/var/tmp/ash/input/"
outdir = "/var/tmp/ash/output/"
geotransform = None
projection = None
sdata_id = ''
workingdir = './'

def float2byte(dataf, min, max):
    dataf_min = np.zeros_like( dataf )
    dataf_max = np.zeros_like( dataf )
    dataf_min[:] = min
    dataf_max[:] = max
    dataf = np.maximum( dataf_min, dataf )
    dataf = np.minimum( dataf_max, dataf )
    
    datab = np.uint8(255*(dataf - min)/(max - min))
    #print(np.nanmin(datab), np.nanmax(datab))
    return datab


def get_file(files, band):
    for file in files:
        if band in file:
            return file
    print("No existe la banda ", band)    
    return None

def leeBanda(path):
    global projection
    global geo_transform
    print("Leyendo ", path)
    ds = gdal.Open(path)
    geo_transform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    data = ds.GetRasterBand(1).ReadAsArray()
    ds = None
    data[data == -999.0] = np.nan
    min = np.nanmin(data)
    max = np.nanmax(data)          
    print(" Min ", min, " Max ", max)
    #print('projection', projection)
    #print('geotransform', geo_transform)
    return data

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
    r = re.search('CG_ABI-L2-([A-Z]{3})', path)
    variable = r.groups(0)[0]
    nc = Dataset(path, 'r')
    data = nc.variables[variable][:].data
    if not projection:
        nx = data.shape[0]
        ny = data.shape[1]
        get_projection(nc, nx, ny)
    return data


def array2raster(newRasterfilename, array):
    print('Guardando ', newRasterfilename)
    #print('projection', projection)
    #print('geotransform', geo_transform)
    cols = array.shape[1]
    rows = array.shape[0]
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfilename, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetProjection(projection)
    outRaster.SetGeoTransform(geo_transform)
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()

    
def array2rasterRGB(newRasterfilename, R, G, B):
    print('Guardando ', newRasterfilename)
    cols = R.shape[1]
    rows = R.shape[0]
    driver = gdal.GetDriverByName('GTiff')
#    outRaster = driver.Create(newRasterfilename, cols, rows, 3, gdal.GDT_Float32)
    outRaster = driver.Create(newRasterfilename, cols, rows, 3, gdal.GDT_Byte)
    outRaster.SetProjection(projection)
    outRaster.SetGeoTransform(geotransform)

    outbandR = outRaster.GetRasterBand(1)
    outbandR.WriteArray(float2byte(R, np.nanmin(R), np.nanmax(R)))
    outbandG = outRaster.GetRasterBand(2)
    outbandG.WriteArray(float2byte(G, np.nanmin(G), np.nanmax(G)))
    outbandB = outRaster.GetRasterBand(3)
    outbandB.WriteArray(float2byte(B, np.nanmin(B), np.nanmax(B)))
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outbandR.FlushCache()
    outbandG.FlushCache()
    outbandB.FlushCache()

    
def main():
    global sdate_id
    
    if len(sys.argv) < 2:
        print("Usanza: ", sys.argv[0], " sYYYYJJJHHMMSSS")
        exit(1)

    # find_files
    sdate_id = sys.argv[1]
    files = glob.glob(datadir+'*'+sdate_id+'*.nc')
    pathC11 = get_file(files, 'C11')
    pathC13 = get_file(files, 'C13')
    pathC15 = get_file(files, 'C15')

    # Obtén datos
    banda11 = leeNC(pathC11)
    banda13 = leeNC(pathC13)
    banda15 = leeNC(pathC15)
    R = np.subtract(banda15, banda13)
    G = np.subtract(banda13, banda11)
    B = banda13

    print("R Min ", np.nanmin(R), " Max ",  np.nanmax(R))
    print("G Min ", np.nanmin(G), " Max ",  np.nanmax(G))
    print("B Min ", np.nanmin(B), " Max ",  np.nanmax(B))
    
    array2rasterRGB(outdir+"goes16.abi.ashrgb-"+sdate_id+'.tif', R, G, B)  
    
if __name__== "__main__":
    main()

