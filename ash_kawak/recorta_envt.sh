#! /bin/bash

if [ ! -z "$1" ]
then
    name=$1
else
    echo "Usanza:  $0 <nombre de archivo GeoTiff o NetCDF original>"
    exit
fi

if [[ ! $name =~ "CMI" ]]; then
    echo "Error: El archivo debe ser nivel L2 variable CMI"
    exit 1
fi

bname=$(basename $name)
extension="${bname##*.}"
filename="${bname%.*}"
outname=$filename-envt.tif

if test -f "$outname"; then
    echo "Error: El archivo $outname ya existe."
    exit 1
fi

# Resolución de salida: 1km 2km 0.5km
# Si el original es 2km y outres es 1km, o viceversa, se remuestrea 
outres="2km"

if [ "$outres" = "2km" ]; then
    ox=2500
    oy=1500
    x=276
    y=33
    w=662
    h=347
elif [ "$outres" = "1km" ]; then
    ox=5000
    oy=3000
    x=552
    y=66
    w=1324
    h=695
else
    echo "Resolución inválida $outres"
    exit 1
fi

if [ "$extension" = "nc" ]; then
    rm tmp.tif
    # primero convierte a GeoTiff
    gdal_translate -of GTiff -ot float32 -unscale -a_srs "+proj=geos +h=35786023.0 +ellps=GRS80 +lat_0=0.0 +lon_0=-75.0 +sweep=x +no_defs" NETCDF:$name:CMI tmp.tif
elif [ "$extension" = "tif" ]; then
    cp $name tmp.tif
else
    echo "Archivo de entrada inválido $name"
    exit 1
fi

# Define si hace falta remuestrear
res=$(gdalinfo tmp.tif|grep "Pixel Size"|cut -d '(' -f 2|cut -d '.' -f 1)
resy=$(gdalinfo tmp.tif|grep "Pixel Size"|cut -d ',' -f 2|cut -d '.' -f 1)
echo "Res $res $resy"
if  [ "$res" == "1002" ] && [ "$outres" == "2km" ]; then
    echo "Remuestreando 1km > 2km"
    mv tmp.tif tmp0.tif
    #gdalwarp -tr 2004.017315487541055 2004.017315487541055 -r bilinear tmp0.tif tmp.tif
    gdalwarp -ts $ox $oy -r bilinear tmp0.tif tmp.tif
    resy=$(gdalinfo tmp.tif|grep "Pixel Size"|cut -d ',' -f 2|cut -d '.' -f 1)
elif  [ "$res" == "2004" ] && [ "$outres" == "1km" ]; then
    mv tmp.tif tmp0.tif
    #gdalwarp -tr 1002.008657743770527 -1002.008657743770527 -r bilinear tmp0.tif tmp.tif
    gdalwarp -ts $ox $oy -r bilinear tmp0.tif tmp.tif
    resy=$(gdalinfo tmp.tif|grep "Pixel Size"|cut -d ',' -f 2|cut -d '.' -f 1)
fi

if (( resy < 0 )); then
    ((yy=$oy-h-y))
    y=$yy
    echo $y
fi

gdal_translate -srcwin $x $y $w $h tmp.tif $outname
