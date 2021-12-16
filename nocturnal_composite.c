/* Nocturnal composite image generation
 * Copyright (c) 2019  Alejandro Aguilar Sierra (asierra@unam.mx)
 * Labotatorio Nacional de Observación de la Tierra, UNAM
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#include "datanc.h"
#include "image.h"
#include "paleta.h"
#include "reader_png.h"


double sun_zenith_angle01(float la, float lo, DataNC datanc)
{
  // input data:
  double UT;
  int Day;
  int Month;
  int Year;
  double Dt;
  double Longitude;
  double Latitude;
  double Pressure;
  double Temperature;

  //output data
  double RightAscension;
  double Declination;
  double HourAngle;
  double Zenith;
  double Azimuth;
  
  //auxiliary
  double t, te, wte, s1, c1, s2, c2, s3, c3, s4, c4,
    sp, cp, sd, cd, sH, cH, se0, ep, De, lambda, epsi,
    sl, cl, se, ce, L, nu, Dlam;
  int yt, mt;

  double PI = M_PI;
  double PI2 = 2*M_PI;
  double PIM = M_PI_2;


  UT = datanc.hour + datanc.min/60.0 + datanc.sec/3600.0;;
  Day = datanc.day;
  Month = datanc.mon;
  Year = datanc.year;
  Longitude = lo*PI/180.0;
  Latitude = la*PI/180;

  Pressure = 1;
  Temperature = 0;
  
  if (Month <= 2) {
    mt = Month + 12;
    yt = Year - 1;
  } else {
    mt = Month;
    yt = Year;
  }

  t = (double)((int)(365.25*(double)(yt-2000)) + (int)(30.6001*(double)(mt+1)) - (int)(0.01*(double)(yt)) + Day) + 0.0416667*UT - 21958.0;
  Dt = 96.4 + 0.00158*t;
  te = t + 1.1574e-5*Dt;

  wte = 0.017202786*te;

  s1 = sin(wte);
  c1 = cos(wte);
  s2 = 2.0*s1*c1;
  c2 = (c1+s1)*(c1-s1);

  RightAscension = -1.38880 + 1.72027920e-2*te + 3.199e-2*s1 - 2.65e-3*c1 + 4.050e-2*s2 + 1.525e-2*c2;
  RightAscension = fmod(RightAscension, PI2);
  if (RightAscension < 0.0) RightAscension += PI2;

  Declination = 6.57e-3 + 7.347e-2*s1 - 3.9919e-1*c1 + 7.3e-4*s2 - 6.60e-3*c2;

  HourAngle = 1.75283 + 6.3003881*t + Longitude - RightAscension;
  HourAngle = fmod(HourAngle + PI, PI2) - PI;
  if (HourAngle < -PI) HourAngle += PI2;
  
  sp = sin(Latitude);
  cp = sqrt((1-sp*sp));
  sd = sin(Declination);
  cd = sqrt(1-sd*sd);
  sH = sin(HourAngle);
  cH = cos(HourAngle);
  se0 = sp*sd + cp*cd*cH;
  ep = asin(se0) - 4.26e-5*sqrt(1.0-se0*se0);
  Azimuth = atan2(sH, cH*sp - sd*cp/cd);
  /*
  if (ep > 0.0)
    De = (0.08422*Pressure) / ((273.0+Temperature)*tan(ep + 0.003138/(ep + 0.08919)));
    else*/
    De = 0.0;

  Zenith = PIM - ep - De;

  return Zenith;
}


double sun_zenith_angle(float la, float lo, DataNC datanc)
{
  // input data:
  double UT;
  int Day;
  int Month;
  int Year;
  double Dt;
  double Longitude;
  double Latitude;
  double Pressure;
  double Temperature;

  //output data
  double RightAscension;
  double Declination;
  double HourAngle;
  double Zenith;
  double Azimuth;
  
  //auxiliary
  double t, te, wte, s1, c1, s2, c2, s3, c3, s4, c4,
    sp, cp, sd, cd, sH, cH, se0, ep, De, lambda, epsi,
    sl, cl, se, ce, L, nu, Dlam;
  int yt, mt;

  double PI = M_PI;
  double PI2 = 2*M_PI;
  double PIM = M_PI_2;


  UT = datanc.hour + datanc.min/60.0 + datanc.sec/3600.0;
  Day = datanc.day;
  Month = datanc.mon;
  Year = datanc.year;
  Longitude = lo*PI/180.0;
  Latitude = la*PI/180;

  Pressure = 1;
  Temperature = 0;
  
  if (Month <= 2) {
    mt = Month + 12;
    yt = Year - 1;
  } else {
    mt = Month;
    yt = Year;
  }

  t = (double)((int)(365.25*(double)(yt-2000)) + (int)(30.6001*(double)(mt+1)) - (int)(0.01*(double)(yt)) + Day) + 0.0416667*UT - 21958.0;
  Dt = 96.4 + 0.00158*t;
  te = t + 1.1574e-5*Dt;

  wte = 0.0172019715*te;

  s1 = sin(wte);
  c1 = cos(wte);
  s2 = 2.0*s1*c1;
  c2 = (c1+s1)*(c1-s1);
  s3 = s2*c1 + c2*s1;
  c3 = c2*c1 - s2*s1;

  L = 1.7527901 + 1.7202792159e-2*te + 3.33024e-2*s1 - 2.0582e-3*c1 + 3.512e-4*s2 - 4.07e-5*c2 + 5.2e-6*s3 - 9e-7*c3 -8.23e-5*s1*sin(2.92e-5*te) + 1.27e-5*sin(1.49e-3*te - 2.337) + 1.21e-5*sin(4.31e-3*te + 3.065) + 2.33e-5*sin(1.076e-2*te - 1.533) + 3.49e-5*sin(1.575e-2*te - 2.358) + 2.67e-5*sin(2.152e-2*te + 0.074) + 1.28e-5*sin(3.152e-2*te + 1.547) + 3.14e-5*sin(2.1277e-1*te - 0.488);

  nu = 9.282e-4*te - 0.8;
  Dlam = 8.34e-5*sin(nu);
  lambda = L + PI + Dlam;

  epsi = 4.089567e-1 - 6.19e-9*te + 4.46e-5*cos(nu);

  sl = sin(lambda);
  cl = cos(lambda);
  se = sin(epsi);
  ce = sqrt(1-se*se);

  RightAscension = atan2(sl*ce, cl);
  if (RightAscension < 0.0) 
    RightAscension += PI2;

  Declination = asin(sl*se);

  HourAngle = 1.7528311 + 6.300388099*t + Longitude - RightAscension + 0.92*Dlam;
  HourAngle = fmod(HourAngle + PI, PI2) - PI;
  if (HourAngle < -PI) HourAngle += PI2;

  sp = sin(Latitude);
  cp = sqrt((1-sp*sp));
  sd = sin(Declination);
  cd = sqrt(1-sd*sd);
  sH = sin(HourAngle);
  cH = cos(HourAngle);
  se0 = sp*sd + cp*cd*cH;
  ep = asin(se0) - 4.26e-5*sqrt(1.0-se0*se0);
  Azimuth = atan2(sH, cH*sp - sd*cp/cd);

  if (ep > 0.0)
    De = (0.08422*Pressure) / ((273.0+Temperature)*tan(ep + 0.003138/(ep + 0.08919)));
  else
    De = 0.0;

  Zenith = PIM - ep - De;

  return Zenith;
}  


ImageData create_nocturnal_composite(DataNC datanc, DataNCF navla, DataNCF navlo)
{
  ImageData imout;
  imout.bpp = 4;
  imout.width = datanc.width;
  imout.height = datanc.height;
  imout.data = malloc(imout.bpp*datanc.size);

  char *fondo_fn;
  if (datanc.width == 2500) 
    fondo_fn = "/usr/local/share/lanot/images/land_lights_2012_conus.png";
  else
    fondo_fn = "/usr/local/share/lanot/images/land_lights_2012_fd.png";
  
  ImageData fondo = reader_image_png(fondo_fn);

  float max_ir_temp = 263.15;  // Para temperaturas menores a esta, la imagen es opaca
  //int i_max = (int)((max_ir_temp - datanc.add_offset)/datanc.scale_factor);
  float tmin=1e10, tmax=-1e10, rmin=1e10, rmax=-1e10;

  double start = omp_get_wtime();

  #pragma omp parallel for shared(datanc, data)
  for (int y=0; y < datanc.height; y++) {
    for (int x=0; x < datanc.width; x++) {
      int i = y*datanc.width + x;
      int pf = i*fondo.bpp;
      int po = i*imout.bpp;
      unsigned char r, g, b, a;
      
      r = g = b = 0;
      a = 0; 
      if (datanc.data_in[i] >= 0 && datanc.data_in[i] < 4095) {
	float rad = datanc.scale_factor*datanc.data_in[i] + datanc.add_offset;
	float f = ( datanc.planck_fk2 / ( log((datanc.planck_fk1 / rad) + 1 )) - datanc.planck_bc1) / datanc.planck_bc2;
	if (f < tmin)
	  tmin = f;
	if (f > tmax)
	  tmax = f;	
	int t;
	for (t = 0; t < 255; t++)
	  if (f >= paleta[t].d && f < paleta[t+1].d)
	    break;
	r = (unsigned char)(255*paleta[t].r);
	g = (unsigned char)(255*paleta[t].g);
	b = (unsigned char)(255*paleta[t].b);   
	   
	if (f > max_ir_temp) {
	  float w = 1. - paleta[t].a;
	  r = (unsigned char)(r*(1 - w) + w * fondo.data[pf]);
          g = (unsigned char)(g*(1 - w) + w * fondo.data[pf+1]);
          b = (unsigned char)(b*(1 - w) + w * fondo.data[pf+2]);
	}
     
	// Para la penumbra, usa geometría solar    
	float w = 0;
	float la = navla.data_in[i];
	float lo = navlo.data_in[i];
	double sza = sun_zenith_angle(la, lo, datanc)*180/M_PI;
      
	if (sza > 88.0)
	  w = 1;
	else if (78.0 < sza && sza < 88.0) {
	  w = (sza - 78.0)/10.0;
	} else
	  w = 0;
      /*/
       // Franjas de penumbra
      float d = 0.25;
      if (90 - d < sza && sza < 90 + d) {
	w = 1;
	g = b = 0;
	r = 255;
      } else
      if (85 - d < sza && sza < 85 + d) {
	w = 1;
	r = b = 0;
	g = 255;
      } else
      if (95 - d < sza && sza < 95 + d) {
	w = 1;
	g = r = 0;
	b = 255;
	}*/ 
	a = (unsigned char)(255*w);
      } else 
	a = 0;
      imout.data[po]   = r;
      imout.data[po+1] = g;
      imout.data[po+2] = b;
      imout.data[po+3] = a;	
    }
  }
  printf("tmin %g tmax %g\n", tmin, tmax);
  double end = omp_get_wtime();
  printf("Tiempo pseudo %lf\n",end - start);
  
  return imout;
}

