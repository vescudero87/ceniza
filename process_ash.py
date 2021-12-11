'''
Este codigo hace ceniza'''
import funtions_ceniza
import sys
import glob
import numpy as np
from osgeo import gdal,osr
path_input="D:\\PROY_CENIZA_GIT\\ceniza\\input\\"
path_output="D:\PROY_CENIZA_GIT\ceniza\output\\"
#Ultimo netCDF
print ("Listando bandas")
b04nc=funtions_ceniza.list_file(path_input,'C04_')
b07nc=funtions_ceniza.list_file(path_input,'C07_')
b11nc=funtions_ceniza.list_file(path_input,'C11_')
b13nc=funtions_ceniza.list_file(path_input,'C13_')
b14nc=funtions_ceniza.list_file(path_input,'C14_')
b15nc=funtions_ceniza.list_file(path_input,'C15_')
#Lee netCDF
print ("Netcdf to NP")
b04 = funtions_ceniza.leeNC(b04nc,"CMI")
b07 = funtions_ceniza.leeNC(b07nc,"CMI")
b11 = funtions_ceniza.leeNC(b11nc,"CMI")
b13 = funtions_ceniza.leeNC(b13nc,"CMI")
b14 = funtions_ceniza.leeNC(b14nc,"CMI")
b15 = funtions_ceniza.leeNC(b15nc,"CMI")
#Algoritmo
print ("Aplicando algorítmo")
a = np.subtract(b13, b15)
b = np.subtract(b11, b13)
c = np.subtract(b07, b13)

ds_ref=gdal.Open(b04nc)

umbnigth = funtions_ceniza.ceniza_umbral(a,b,c,b14,ds_ref)
print ("Algoritmo terminado")
#Crea tif Geostacionario

print ("Creando TIF")
funtions_ceniza.creaTif(ds_ref, umbnigth,path_output+"prueba.tif")
