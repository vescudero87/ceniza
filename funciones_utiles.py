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

def plot(pathInput, pathOutput):
    
    print('Procesando: '+pathInput)
    ds, data = tifToNumpy(pathInput)
    extension, nx, ny = obtieneExtension(ds)
    #cpt = loadCPT('./paletas/IR4AVHRR6.cpt')
    #cpt_convert = LinearSegmentedColormap('cpt', cpt)
    # make a color map of fixed colors
    cmap = colors.ListedColormap(['#000000','#000000','#000000', '#0000ff', '#0000ff', '#296edf', '#00ffff', '#00ff00', '#2ec659', '#ffff00', '#ffa500', '#be2c04', '#fb6238', '#fb6238', '#ff0000', '#ff0083', '#ed70ed', '#ed70ed', '#f7c0de', '#f7>    #bounds=[0,6000,7000,8000,9000,10000,11000,12000,13000,14000,15000,16000,17000,18000,19000,20000,21000,22000,23000,24000]
    bounds=[0,11000,12000,13000,14000,15000,16000,17000]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    px = 1/plt.rcParams['figure.dpi']  # pixel in inches
    fig = plt.figure(figsize=(nx*px, ny*px))
    ax = plt.axes([0,0,1,1],projection=crrs.PlateCarree(),frameon=False)

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)    
    plt.autoscale(tight=True) 
    plt.gca().outline_patch.set_visible(False)

    ax.set_extent([extension[0],extension[2],extension[3],extension[1]], crs=crrs.PlateCarree())

    plt.imshow(data,extent=[extension[0],extension[2],extension[3],extension[1]], vmin=11000, vmax=18000, cmap=cmap)

    cax = fig.add_axes([0.01,0.99,0.98,0.01])
    cbar = plt.colorbar( cax=cax, orientation='horizontal')
    cbar.ax.tick_params(labelsize=10, labelcolor ='white' , grid_alpha=0.5)
    cbar.outline.set_linewidth(1)

    name = pathOutput+pathInput.split('/')[-1].split('.tif')[0]+'.png'

    plt.savefig(name,dpi=300,bbox_inches='tight', pad_inches=0)