from importlib.resources import path


def creaTif(dsRef,npy,output):
    geotransform = dsRef.GetGeoTransform()
    nx = dsRef.RasterXSize
    ny = dsRef.RasterYSize
    dst_ds = gdal.GetDriverByName('GTiff').Create(output, ny, nx, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(geotransform)
    srs = osr.SpatialReference()
    srs.ImportFromWkt(dsRef.GetProjectionRef())
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.GetRasterBand(1).WriteArray(npy)
    dst_ds.FlushCache()
    dst_ds = None

def obtieneCuadrante(ds):
    xSize = ds.RasterXSize
    ySize = ds.RasterYSize
    geo = ds.GetGeoTransform()
    xmin = geo[0]
    ymax = geo[3]
    xres = geo[1]
    yres = geo[5]
    xmax = xmin + xres*xSize
    ymin = ymax + yres*ySize

    return [xmin,ymax,xmax,ymin]

def obtieneParametrosGeoTrasform(ds):
    geo = ds.GetGeoTransform()
    nx = ds.RasterXSize
    ny = ds.RasterYSize
    xmin = geo[0]
    ymax = geo[3]
    xres = geo[1]
    yres = geo[5]
    xmax = xmin + xres*nx
    ymin = ymax + yres*ny

    return nx,ny,xmin,ymax,xres,yres,xmax,ymin


def remuestrea(pathOutput,ds,dimx,dimy):
    gdal.Translate(pathOutput,ds,options=gdal.TranslateOptions(xRes=dimx,yRes=dimy))

def RGB(r,g,b,tile,anio,fecha,fechaProc,pathOutputGeoTiff,pathOutputPeta):
    nombre = pathOutputGeoTiff+'sargazo/'+tile+'/'+'S2_MSI_SAR_'+tile+'_'+fecha+'_'+fechaProc+".tif"
    os.system('gdal_merge.py -separate -co PHOTOMETRIC=RGB -o '+nombre+' '+r+' '+g+' '+b)
    # MANDA A PETA
    os.system('scp '+nombre+' lanotadm@stratus:'+pathOutputPeta+'l2/geotiff/sargazo/'+tile+'/')

def reproyeccion(pathInput, pathOuput):
    os.system('gdalwarp -t_srs EPSG:4326 '+pathInput+' '+pathOuput)

def recorte(cuadrante, pathInput, pathOutput):
    # cuandrante ulx uly lrx lry
    os.system('gdal_translate -projwin '+str(cuadrante[0])+' '+str(cuadrante[1])+' '+str(cuadrante[2])+' '+str(cuadrante[3])+' '+pathInput+' '+pathOutput)
