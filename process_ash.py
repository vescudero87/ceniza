'''
Este codigo hace ceniza'''
import funtions
import sys
import glob
import numpy as np
if len(sys.argv) < 2:
    print("Usanza: ", sys.argv[0], " <sYYYYjjjhhmm>")
    exit(1)

# find_files
sdate_id = sys.argv[1]
files = glob.glob(datadir+'*'+sdate_id+'*.nc')
pathC11 = funtions.funtions.get_file(files, 'C11')
pathC13 = funtions.get_file(files, 'C13')
pathC14 = funtions.get_file(files, 'C14')
pathC15 = funtions.get_file(files, 'C15')
#    pathLST = funtions.get_file(files, 'LST')

b11 = funtions.leeNC(pathC11)
b13 = funtions.leeNC(pathC13)
b14 = funtions.leeNC(pathC14)
b15 = funtions.leeNC(pathC15)

a = np.subtract(b13, b15)
b = np.subtract(b14, b15)

a = np.where(a <= 0, 1.0, 0.0)
b = np.where(b <= 0, 1.0, 0.0)
c = np.where((a == 1) & (b == 1), 1.0, 0.0)
d = np.subtract(b13, b11)
d = np.where(d <= 0.5, 1.0, 0.0)
e = np.where((c == 1) & (d == 1), 1.0, 0.0)

#blst = np.where((blst > 273.15) & (blst < 283.15), 0.0, blst)

#sat.sensor.prod-YYYY.MMDD.HHmm
funtions.array2raster(outdir+"goes16.abi.ASH-"+sdate_id+'.tif', e)
funtions.array2raster(outdir+"goes16.abi.13_15-"+sdate_id+'.tif', a)
funtions.array2raster(outdir+"goes16.abi.14_15-"+sdate_id+'.tif', b)
funtions.array2raster(outdir+"goes16.abi.C-"+sdate_id+'.tif', c)
funtions.array2raster(outdir+"goes16.abi.D-"+sdate_id+'.tif', d)
