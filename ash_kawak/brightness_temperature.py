#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import glob
import numpy as np
from osgeo import gdal, osr
from netCDF4 import Dataset


# Variables globales
sdata_id = ''
workingdir = '/var/tmp/'
destPath = '/var/tmp/'
inputPath = '/home/ceniza/netcdf_conus/'
bandaPath = ''
geo_transform = None
projection = None
loW = -106.8133292
loE = -94.2550041
laN = 22.4665102
laS = 15.1901564


def get_file(files, band):
    for file in files:
        if band in file:
            return file
    print("No existe la banda ", band)
    exit(1)
    return 'Error'


def array2raster(newRasterfilename, array):
    print('Guardando ', newRasterfilename)
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


def recortaBanda(path, banda, calibra):
    print('Recortando ', path)
    global sdate_id
    global destPath
    global geo_transform
    global projection

    os.chdir(workingdir)
    bandaPath = destPath+banda+'.'+'bt'+'.'+sdate_id+'.tif'
    if os.path.isfile('tmp.tif'):
        os.remove('tmp.tif')
    os.system("gdal_translate -of GTiff -ot float32 -unscale NETCDF:"+path+":Rad tmp.tif")
    os.system("gdalwarp -overwrite -CO COMPRESS=deflate -t_srs EPSG:4326 -dstnodata -999.0 -tr 0.01874377 0.01810038 tmp.tif tmp4326.tif")
    extent = "-te {} {} {} {} ".format(loW,laS,loE,laN)
    os.system("gdalwarp -overwrite "+extent+" -tr 0.01874377 0.01810038 tmp4326.tif " + bandaPath)  
    ds = gdal.Open(bandaPath)
    geo_transform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    data = ds.GetRasterBand(1).ReadAsArray()
    ds = None
    data[data == -999.0] = np.nan
    if calibra:
        nc = Dataset(path)
        planck_fk1 = nc.variables['planck_fk1'][:]
        planck_fk2 = nc.variables['planck_fk2'][:]
        planck_bc1 = nc.variables['planck_bc1'][:]
        planck_bc2 = nc.variables['planck_bc2'][:]
        nc.close        
        data = ( planck_fk2 / ( np.log((planck_fk1 / data) + 1 )) - planck_bc1) / planck_bc2
        array2raster(bandaPath, data)
    min = np.nanmin(data)
    max = np.nanmax(data)
    print(banda, " Min ", min, " Max ", max)
    return data


def main():
    global sdate_id

    if len(sys.argv) < 2:
        print("Usanza: ", sys.argv[0], " sYYYYJJJHHMMSSS")
        exit(1)

    # find_files
    sdate_id = sys.argv[1]
    files = glob.glob(inputPath+'*'+sdate_id+'*.nc')
    pathC07 = get_file(files, 'C07')
    pathC08 = get_file(files, 'C08')
    pathC09 = get_file(files, 'C09')
    pathC10 = get_file(files, 'C10')
    pathC11 = get_file(files, 'C11')
    pathC12 = get_file(files, 'C12')
    pathC13 = get_file(files, 'C13')
    pathC14 = get_file(files, 'C14')
    pathC15 = get_file(files, 'C15')
    pathC16 = get_file(files, 'C16')

    # Georreferencia, recorta y obtén datos
    banda07 = recortaBanda(pathC07, 'C07', True)
    banda08 = recortaBanda(pathC08, 'C08', True)
    banda09 = recortaBanda(pathC09, 'C09', True)
    banda10 = recortaBanda(pathC10, 'C10', True)
    banda11 = recortaBanda(pathC11, 'C11', True)
    banda12 = recortaBanda(pathC12, 'C12', True)
    banda13 = recortaBanda(pathC13, 'C13', True)
    banda14 = recortaBanda(pathC14, 'C14', True)
    banda15 = recortaBanda(pathC15, 'C15', True)
    banda16 = recortaBanda(pathC16, 'C16', True)

if __name__== "__main__":
    main()
