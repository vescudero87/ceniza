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

def tif2array(path_aux,band):
    dsr = gdal.Open(path_aux+"*"+band+"*")
    np_array = np.array(dsr.ReadAsArray())
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
"""""
def ceniza_umbral(a,b,c,b14,b04,ds,dobj):
    cenum=np.zeros(a.shape)
    nx=a.shape[0]
    ny=a.shape[1]
    for i in range(nx):
        for j in range(ny):
            #Calcula angulo zenital
            #print ("Aplicando umbrales para dia noche y crepusculo")
            sun_zenith=lat_log(ds,i,j,dobj)
            if ((a[i,j] <= 0) and (b[i,j] >= 0) and (c[i,j] >= 2) and sun_zenith > 90):
                cenum[i,j]=1
            elif ((a[i,j] <= 1) and (b[i,j] >= -0.5) and (c[i,j] >= 2) and sun_zenith > 90):
                cenum[i,j]=2
            elif ((a[i,j] <= 3) and (b[i,j] >= -1) and (c[i,j] >= 2) and (b14[i,j] < 273) and sun_zenith > 90):
                cenum[i,j]=3
            elif ((a[i,j] <= 0) and (b[i,j] >= 0) and (c[i,j] >= 2) and (b04[i,j] >= 0.002) and sun_zenith < 90 and sun_zenith > 70):
                cenum[i,j]=1
            elif ((a[i,j] <= 1) and (b[i,j] >= -0.5) and (c[i,j] >= 2) and (b04[i,j] >= 0.002) and (b14[i,j] < 273) and sun_zenith < 90 and sun_zenith > 70):
                cenum[i,j]=2
            elif ((a[i,j] <= 3) and (b[i,j] >= -1) and (c[i,j] >= 2) and (b04[i,j] >= 0.002) and (b14[i,j] < 273) and sun_zenith < 90 and sun_zenith > 70):
                cenum[i,j]=3
            elif ((a[i,j] <= 0) and (b[i,j] >= 0) and (c[i,j] >= 2) and (b04[i,j] >= 0.002) and sun_zenith < 70):
                cenum[i,j]=1
            elif ((a[i,j] <= 1) and (b[i,j] >= -0.5) and (c[i,j] >= 2) and (b04[i,j] >= 0.002) and sun_zenith < 70):
                cenum[i,j]=2
            elif ((a[i,j] <= 3) and (b[i,j] >= -1) and (c[i,j] >= 2) and (b04[i,j] >= 0.002) and (b14[i,j] < 273) and sun_zenith < 70):
                cenum[i,j]=3
            else: 
                cenum[i,j]=0
    return cenum
"""
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
"""""
def lat_log(ds,fila,columna,dobj):
    nx,ny,xmin,ymax,xres,yres,xmax,ymin = funciones_utiles.obtieneParametrosGeoTrasform(ds)
    xgeo=(columna * xres) + xmin +xres
    ygeo=(fila * yres) + ymin +yres
    transformer = Transformer.from_crs("+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs","EPSG:4326", always_xy=True)
    xlong_ylat=transformer.transform(xgeo, ygeo)
    lat=xlong_ylat[1]
    long=xlong_ylat[0]
    #print ("Calculando Sun zentih")
    sun_zenith=prue_cenith(lat,long,dobj)
    return sun_zenith
#    print(xres, xmin, yres, ymin)
#    print(xlong_ylat)
#    print (xgeo,ygeo)

def prue_cenith(lat,long,dobj):
#    dobj = datetime.datetime.now(datetime.timezone.utc)
    sza = float(90) - get_altitude(lat, long, dobj)
    return sza
#    print ("Angulo Zenital" sza)

def get_time(file):
    date_split=file.split("\\")[-1].split("_")[3].split("s")[1][:-3]
    date_time=datetime.datetime.strptime(date_split,"%Y%j%H%M")
    date_time = date_time.replace(tzinfo=pytz.UTC)
    return date_time
"""
