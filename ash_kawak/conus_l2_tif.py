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
    bandaPath = destPath+banda+'.'+'.'+sdate_id+'.tif'
    if os.path.isfile('tmp.tif'):
        os.remove('tmp.tif')
    os.system("gdal_translate -of GTiff -ot float32 -unscale NETCDF:"+path+" tmp.tif")
    os.system("gdalwarp -overwrite -CO COMPRESS=deflate -t_srs EPSG:4326 -dstnodata -999.0 -tr 0.01874377 0.01810038 tmp.tif tmp4326.tif")
    extent = "-te {} {} {} {} ".format(loW,laS,loE,laN)
    os.system("gdalwarp -overwrite "+extent+" -tr 0.01874377 0.01810038 tmp4326.tif " + bandaPath)
    ds = gdal.Open(bandaPath)
    geo_transform = ds.GetGeoTransform()
    projection = ds.GetProjection()
    data = ds.GetRasterBand(1).ReadAsArray()
    ds = None
    data[data == -999.0] = np.nan

def main():
    global sdate_id

    if len(sys.argv) < 2:
        print("Usanza: ", sys.argv[0], " sYYYYJJJHHMMSSS")
        exit(1)

    # find_files
    sdate_id = sys.argv[1]
    files = glob.glob(inputPath+'*'+sdate_id+'*.nc')
    pathACHAC-M3 = get_file(files, 'ACHAC-M3')
    pathCHTC-M3 = get_file(files, 'CHTC-M3')
    pathACMC-M3 = get_file(files, 'ACMC-M3')
    pathACTPC-M3 = get_file(files, 'ACTPC-M3')
    pathADPC-M3 = get_file(files, 'ADPC-M3')
    pathAODC-M3 = get_file(files, 'AODC-M3')
    pathCMIPC-M3C01 = get_file(files, 'CMIPC-M3C01')
    pathCMIPC-M3C02 = get_file(files, 'CMIPC-M3C02')
    pathCMIPC-M3C03 = get_file(files, 'CMIPC-M3C03')
    pathCMIPC-M3C04 = get_file(files, 'CMIPC-M3C04')
    pathCMIPC-M3C05 = get_file(files, 'CMIPC-M3C05')
    pathCMIPC-M3C06 = get_file(files, 'CMIPC-M3C06')
    pathCMIPC-M3C07 = get_file(files, 'CMIPC-M3C07')
    pathCMIPC-M3C08 = get_file(files, 'CMIPC-M3C08')
    pathCMIPC-M3C09 = get_file(files, 'CMIPC-M3C09')
    pathCMIPC-M3C10 = get_file(files, 'CMIPC-M3C10')
    pathCMIPC-M3C11 = get_file(files, 'CMIPC-M3C11')
    pathCMIPC-M3C12 = get_file(files, 'CMIPC-M3C12')
    pathCMIPC-M3C13 = get_file(files, 'CMIPC-M3C13')
    pathCMIPC-M3C14 = get_file(files, 'CMIPC-M3C14')
    pathCCMIPC-M3C15 = get_file(files, 'CMIPC-M3C15')
    pathCMIPC-M3C16 = get_file(files, 'CMIPC-M3C16')
    pathCODDC-M3 = get_file(files, 'CODDC-M3')
    pathCODNC-M3 = get_file(files, 'CODNC-M3')
    pathCPSDC-M3 = get_file(files, 'CPSDC-M3')
    pathCCPSNC-M3 = get_file(files, 'CPSNC-M3')
    pathCTPC-M3 = get_file(files, 'CTPC-M3')
    pathLSTC-M3 = get_file(files, 'LSTC-M3')
    pathNAVC-M3 = get_file(files, 'NAVC-M3')

 # Georreferencia, recorta y obtén datos
    bandaACHAC-M3 = recortaBanda(pathACHAC-M3, 'ACHAC-M3', True)
    bandaCHTC-M3 = recortaBanda(pathCHTC-M3, 'CHTC-M3', True)
    bandaACMC-M3 = recortaBanda(pathACMC-M3, 'ACMC-M3', True)
    bandaACTPC-M3 = recortaBanda(pathACTPC-M3, 'ACTPC-M3', True)
    bandaADPC-M3 = recortaBanda(pathADPC-M3, 'ADPC-M3', True)
    bandaAODC-M3 = recortaBanda(pathAODC-M3, 'AODC-M3', True)
    bandaCMIPC-M3C01 = recortaBanda(pathCMIPC-M3C01, 'CMIPC-M3C01', True)
    bandaCMIPC-M3C02 = recortaBanda(pathCMIPC-M3C02, 'CMIPC-M3C02', True)
    bandaCMIPC-M3C03 = recortaBanda(pathCMIPC-M3C03, 'CMIPC-M3C03', True)
    bandaCMIPC-M3C04 = recortaBanda(pathCMIPC-M3C04, 'CMIPC-M3C04', True)
    bandaCMIPC-M3C05 = recortaBanda(pathCMIPC-M3C05, 'CMIPC-M3C05', True)
    bandaCMIPC-M3C06 = recortaBanda(pathCMIPC-M3C06, 'CMIPC-M3C06', True)
    bandaCMIPC-M3C07 = recortaBanda(pathCMIPC-M3C07, 'CMIPC-M3C07', True)
    bandaCMIPC-M3C08 = recortaBanda(pathCMIPC-M3C08, 'CMIPC-M3C08', True)
    bandaCMIPC-M3C09 = recortaBanda(pathCMIPC-M3C09, 'CMIPC-M3C09', True)
    bandaCMIPC-M3C10 = recortaBanda(pathCMIPC-M3C10, 'CMIPC-M3C10', True)
    bandaCMIPC-M3C11 = recortaBanda(pathCMIPC-M3C11, 'CMIPC-M3C11', True)
    bandaCMIPC-M3C12 = recortaBanda(pathCMIPC-M3C12, 'CMIPC-M3C12', True)
    bandaCMIPC-M3C13 = recortaBanda(pathCMIPC-M3C13, 'CMIPC-M3C13', True)
    bandaCMIPC-M3C14 = recortaBanda(pathCMIPC-M3C14, 'CMIPC-M3C14', True)
    bandaCMIPC-M3C15 = recortaBanda(pathCMIPC-M3C15, 'CMIPC-M3C15', True)
    bandaCMIPC-M3C16 = recortaBanda(pathCMIPC-M3C16, 'CMIPC-M3C16', True)
    bandaCODDC-M3 = recortaBanda(pathCODDC-M3, 'CODDC-M3', True)
    bandaCODNC-M3 = recortaBanda(pathCODNC-M3, 'CODNC-M3', True)
    bandaCPSDC-M3 = recortaBanda(pathCPSDC-M3, 'CPSDC-M3', True)
    bandaCPSNC-M3 = recortaBanda(pathCPSNC-M3, 'CPSNC-M3', True)
    bandaCTPC-M3 = recortaBanda(pathCTPC-M3, 'CTPC-M3', True)
    bandaLSTC-M3 = recortaBanda(pathLSTC-M3, 'LSTC-M3', True)
    bandaNAVC-M3 = recortaBanda(pathNAVC-M3, 'NAVC-M3', True)

if __name__== "__main__":
    main()
