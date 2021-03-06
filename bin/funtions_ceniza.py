import os
import re
import sys
import funciones_utiles
from pysolar.solar import *
import datetime
from glob import glob
import numpy as np
from scipy.signal import convolve2d
from osgeo import gdal,osr
from netCDF4 import Dataset
from pyproj import Transformer
import pytz


def get_date(file):
    date_split=file.split("\\")[-1].split("_")[3].split("s")[1][:-7]
    return date_split

def get_time(file):
    time_split=file.split("\\")[-1].split("_")[3].split("s")[1][7:-3]
    return time_split


def sun_zenith(date,time,path_input):
    os.chdir(path_input)
    os.system("sun_zenith_angle_map_conus "+date+" "+time)


def list_file_tif(path_sza,band):
    firstfile=glob(path_sza+band+"*")
    firstfile.sort()
    lastif=firstfile[-1]
    return lastif

def tif2array(szatif):
    dsr = gdal.Open(szatif)
    np_array = dsr.GetRasterBand(1).ReadAsArray()
    return np_array

def list_file(path_input,band):
    firstfile=glob(path_input+"*"+band+"*")
    firstfile.sort()
    last=firstfile[-1]
    return last

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

def leeNC(path_input,var):
    nc = Dataset(path_input, 'r')
    data = nc.variables[var][:].data
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

def creaTif(dsRef,npy,output):
    geotransform = dsRef.GetGeoTransform()
    nx = npy.shape[0]
    ny = npy.shape[1]
    print(nx,ny)
    print(npy.shape)
    dst_ds = gdal.GetDriverByName('GTiff').Create(output, ny, nx, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(dsRef.GetProjectionRef())
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.GetRasterBand(1).WriteArray(npy)
    dst_ds.FlushCache()
    dst_ds = None

def reproyeccion(Input,Output):
    os.system('gdalwarp -t_srs EPSG:4326 '+Input+' '+Output)

def get_name(file):
    name_split=file.split("\\")[-1].split("s")[2].split(".")[0].split("nc")
    return name_split[0]
    
def recorte(cuadrante, pathInput, pathOutput):
    # cuandrante ulx uly lrx lry
    os.system('gdal_translate -projwin '+str(cuadrante[0])+' '+str(cuadrante[1])+' '+str(cuadrante[2])+' '+str(cuadrante[3])+' '+pathInput+' '+pathOutput)
