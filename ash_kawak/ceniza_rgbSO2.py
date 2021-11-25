#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import numpy as np
from osgeo import gdal, osr


# Variables globales
sdata_id = ''
workingdir = './'
destPath = './'
inputPath = './'
bandaPath = ''
geo_transform = None
projection = None


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

def leeBanda(path, banda):
    global projection
    global geo_transform
    ds = gdal.Open(path)
    geo_transform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    data = ds.GetRasterBand(1).ReadAsArray()
    ds = None
    data[data == -999.0] = np.nan
    min = np.nanmin(data)
    max = np.nanmax(data)          
    print(banda, " Min ", min, " Max ", max)
    #print('projection', projection)
    #print('geotransform', geo_transform)
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
    outRaster.SetGeoTransform(geo_transform)

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
    files = glob.glob(inputPath+'*'+sdate_id+'*.tif')
    pathC09 = get_file(files, 'C11')
    pathC10 = get_file(files, 'C11')
    pathC11 = get_file(files, 'C11')
    pathC13 = get_file(files, 'C13')

    # Obtén datos
    banda11 = leeBanda(pathC11, 'C11')
    banda13 = leeBanda(pathC13, 'C13')
    banda15 = leeBanda(pathC15, 'C15')
   
    R = np.subtract(banda09, banda10)
    G = np.subtract(banda13, banda11)
    B = banda13

    print("R Min ", np.nanmin(R), " Max ",  np.nanmax(R))
    print("G Min ", np.nanmin(G), " Max ",  np.nanmax(G))
    print("B Min ", np.nanmin(B), " Max ",  np.nanmax(B))
    
    array2rasterRGB(destPath+"ash-rgb"+'.'+sdate_id+'.tif', R, G, B)    
    
if __name__== "__main__":
    main()

