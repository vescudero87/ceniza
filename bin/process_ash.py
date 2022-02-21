'''
Este codigo hace ceniza'''
import funtions_ceniza
import sys
import glob
import numpy as np
from osgeo import gdal,osr
import os
#path_input="D:\\PROY_CENIZA_GIT\\ceniza\\input\\"
#path_output="D:\PROY_CENIZA_GIT\ceniza\output\\"
#path_aux="D:\PROY_CENIZA_GIT\ceniza\auxiliares\\"
path_input="/home/lanotadm/ash/ceniza/input/"
path_output="/home/lanotadm/ash/ceniza/output/"
path_aux="/home/lanotadm/ash/ceniza/auxiliares/"
path_tmp="/home/lanotadm/ash/ceniza/tmp/"

#Ultimo netCDF
print ("Listando bandas")
b04nc=funtions_ceniza.list_file(path_input,'C04_')
b07nc=funtions_ceniza.list_file(path_input,'C07_')
b11nc=funtions_ceniza.list_file(path_input,'C11_')
b13nc=funtions_ceniza.list_file(path_input,'C13_')
b14nc=funtions_ceniza.list_file(path_input,'C14_')
b15nc=funtions_ceniza.list_file(path_input,'C15_')

#Dia y hora de la imagen
date=funtions_ceniza.get_date(b04nc)
print ("Dia de la imagen "+date)

time=funtions_ceniza.get_time(b04nc)
print ("Hora de la imagen "+time)

funtions_ceniza.sun_zenith(date,time,path_tmp)

szatif=funtions_ceniza.list_file_tif(path_tmp,'sza-')

#Obtiene imagen de referencia
os.system("gdal_translate NETCDF:" +b04nc+":CMI ref.tif")
ds_ref=gdal.Open("ref.tif")

#Lee netCDF
print ("Netcdf to NP")
b04 = funtions_ceniza.leeNC(b04nc,"CMI")
b07 = funtions_ceniza.leeNC(b07nc,"CMI")
b11 = funtions_ceniza.leeNC(b11nc,"CMI")
b13 = funtions_ceniza.leeNC(b13nc,"CMI")
b14 = funtions_ceniza.leeNC(b14nc,"CMI")
b15 = funtions_ceniza.leeNC(b15nc,"CMI")


print ("Importando SZA geotif")
sun = funtions_ceniza.tif2array(szatif)

#Algoritmo
print ("Aplicando algorítmo ")
print ("Calculando transmisividad inversa")
a = np.subtract(b13, b15)
b = np.subtract(b11, b13)
c = np.subtract(b07, b13)
print ("Aplicando umbrales")
noche = np.where((a <= 0) & (b >= 0) & (c >= 2), 1.0, (np.where((a <= 1) & (b >= -0.5) & (c >= 2), 2.0, (np.where((a <= 3) & (b >= -1) & (c >= 2) & (b14 < 273), 3.0, 0.0)))))
crepusculo = np.where((a <= 0) & (b >= 0) & (c >= 2) & (b04 >= 0.002), 1.0, (np.where((a <= 1) & (b >= -0.5) & (c >= 2) & (b04 >= 0.002) & (b14 <= 273), 2.0, (np.where((a <= 3) & (b >= -1) & (c >= 2) & (b04 >= 0.002) & (b14 < 273), 3.0, 0.0)))))
dia = np.where((a <= 0) & (b >= 0) & (c >= 2) & (b04 >= 0.002), 1.0, (np.where((a <= 1) & (b >= -0.5) & (c >= 2) & (b04 >= 0.002), 2.0, (np.where((a <= 3) & (b >= -1) & (c >= 2) & (b04 >= 0.002) & (b14 < 273), 3.0, 0.0)))))
ceniza = np.where(sun >= 85,noche, (np.where((sun <= 85) & (sun >= 70),crepusculo, (np.where(sun < 70,dia,0.0)))))

print("Algoritmo terminado")

print ("Creando GEOTIFF Geoestacionario")

funtions_ceniza.creaTif(ds_ref, ceniza, path_tmp+"prueba.tif")

funtions_ceniza.reproyeccion(path_tmp+"prueba.tif",path_tmp+"ceniza_geo.tif")

cuadrante = [-106.8267320, 22.4800015, -94.2686204, 15.2125758]

name = funtions_ceniza.get_name(b04nc)

funtions_ceniza.recorte(cuadrante,path_tmp+"ceniza_geo.tif",path_output+"CG_ABI-L2-Ceniza_s"+name+".tif")

os.system("rm -f *.tif")
