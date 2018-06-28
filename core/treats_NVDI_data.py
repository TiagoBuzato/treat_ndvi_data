#!/opt/anaconda3/envs/py360/bin/python
# -*- coding: utf-8 -*-

'''
    File name: insertMerraData.py
    Python Version: 3.6.0

    ##########   DATAPROCESSOR   ##########
    Ca

'''
from netCDF4._netCDF4 import Dataset

__author__ = "Tiago S. Buzato"
__version__ = "0.1"
__email__ = "tiago.buzato@climatempo.com.br"
__status__ = "Development"

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro


import os
import requests
import glob
import re
import rasterio
import numpy
from configinit.setting import get_rootDir, get_coordinates
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
from multiprocessing import Process

class treats_NVDI_data():
    def __init__(self, building, getting, verbose):

        self.verbose = verbose
        self.download = getting
        self.building = building
        self.base_dir = get_rootDir()
        self.output_NDVI_aqua = self.base_dir+'/output_NDVI_Aqua/'
        self.output_NDVI_terra = self.base_dir + '/output_NDVI_Terra/'
        self.output_images = self.base_dir + '/output_images/'
        self.MXPROCS = 20
        treats_NVDI_data.run(self)

    def scraping_data(self, url, ext, output, verbose):
        if verbose:
            print("[I] -> Scraping data.")
        dataList= self.get_dataList(url, ext, verbose)

        for files in dataList:
            urlretrieve(files, output+files.split('/')[-1])
            print('Got file: ', files)

    def get_dataList(self, url, ext, verbose):
        if verbose:
            print("[I] -> Make Data list from page")
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        dataList = [url + '/' + node.get('href').split('/')[-1] for node in soup.find_all('a') if node.get('href').endswith(ext)]

        return dataList

    def load_image(self, inputFile, region, verbose):
        if verbose:
            print("[I] - Load the both biweekly images.")
        procs = []
        listndvi = glob.glob(inputFile + "M*13Q1.*.250m_16_dias_NDVI_"+region+".tif")
        listndvi = sorted(listndvi)

        #for file in listndvi:
        while len(listndvi)!=0:
            date = self.get_date(listndvi[0], verbose)
            listref = [x for x in listndvi if re.search(date, x)]
            processControl = Process(target=self.build_image, args=(listref, self.output_images, region, verbose))
            procs.append(processControl)
            processControl.start()

            while len(procs) >= self.MXPROCS:
                for thread in procs:
                    procs.remove(thread)
            #self.build_image(listref, self.output_images, region, verbose)

            for rm in listref:
                listndvi.remove(rm)

        return

    def build_image(self, listimage, output_images, region, verbose):
        if verbose:
            print("[I] - Building just one image.")

        #Variables to create netcdf file
        resolution=0.0025
        lonbegin=get_coordinates(region)['upper_left'][0]
        latbegin = get_coordinates(region)['upper_left'][1]

        if len(listimage)==1:
            # Open matrix 1 and 2 from tif images to create newmatrix
            imga = rasterio.open(listimage[0]).read(1)
            newmatrix = imga
            # close all files used
            del imga

        elif len(listimage)==2:
            #Open matrix 1 and 2 from tif images to create newmatrix
            imga = rasterio.open(listimage[0]).read(1)
            imgb = rasterio.open(listimage[1]).read(1)
            newmatrix = numpy.maximum(imga, imgb)
            # close all files used
            del imga
            del imgb

        elif len(listimage)>2:
            return

        #Defined number of column and line over the bigger matrix
        #NC = abs(round(((lonend - lonbegin) / resolution) + 1))
        #NL = abs(round(((latend - latbegin) / resolution) + 1))
        NC = newmatrix.shape[0]
        NL = newmatrix.shape[1]

        #Path where will be save the new netcdf
        #namenewfile = output_images+listimage[0].replace(listimage[0].split(".")[-3], date).replace(listimage[0].split(".")[-1],
        namenewfile = output_images+listimage[0].split('/')[-1].replace('.tif', '_'+listimage[0].split('/')[-2].split('_')[-1])+".nc"

        #New netcdf file
        newfile = Dataset(namenewfile, 'w', format='NETCDF4')

        #Create vetor of latitude and logitude
        new_lat = [latbegin + i *resolution for i in range(0,NL)]
        new_lon = [lonbegin + i *resolution for i in range(0,NC)][::-1]

        #Defined Dimension of netcdf file
        newfile.createDimension("lat", len(new_lat))
        newfile.createDimension("lon", len(new_lon))

        #Defined variables of netcdf file
        latitude = newfile.createVariable("lat","f4",("lat",))
        longitude = newfile.createVariable("lon","f4",("lon",))
        value = newfile.createVariable("value","f4",("lon","lat",))

        #fill netcdf's variables with newmatrix, latitude and logitude vetors
        value[:,:]=newmatrix
        latitude[:]=new_lat
        longitude[:]=new_lon

        newfile.close()

        print("Builded file: ", namenewfile)
        #Delete newmatrix
        del newmatrix

    def get_date(self, namefile, verbose):
        if verbose:
            print("[I] - Get date from file: ", namefile)
        date = (namefile.split(".")[-3])[0:-2]

        return date

    def run(self):
        '''

        :return: list
        '''

        try:
            os.path.isdir(self.output_NDVI_aqua)
            os.path.isdir(self.output_NDVI_terra)
            os.path.isdir(self.output_images)
        except:
            os.mkdir(self.output_NDVI_aqua)
            os.mkdir(self.output_NDVI_terra)
            os.mkdir(self.output_images)

        if self.download:
            url_aqua_sp = 'https://www.modis.cnptia.embrapa.br/BANCO_MODIS/AQUA/SP/NDVI/'
            url_aqua_sul = 'https://www.modis.cnptia.embrapa.br/BANCO_MODIS/AQUA/RS/NDVI/'
            url_terra_sp = 'https://www.modis.cnptia.embrapa.br/BANCO_MODIS/TERRA/SP/NDVI/'
            url_terra_sul = 'https://www.modis.cnptia.embrapa.br/BANCO_MODIS/TERRA/RS/NDVI/'
            ext = 'tif'

            self.scraping_data(url_aqua_sp, ext, self.output_NDVI_aqua, self.verbose)
            self.scraping_data(url_aqua_sul, ext, self.output_NDVI_aqua, self.verbose)
            self.scraping_data(url_terra_sp, ext, self.output_NDVI_terra, self.verbose)
            self.scraping_data(url_terra_sul, ext, self.output_NDVI_terra, self.verbose)

        if self.building:
            terraRS = Process(target=self.load_image, args=(self.output_NDVI_terra, "RS", self.verbose))
            aquaRS = Process(target=self.load_image, args=(self.output_NDVI_aqua, "RS", self.verbose))
            terraSP = Process(target=self.load_image, args=(self.output_NDVI_terra, "SP", self.verbose))
            aquaSP = Process(target=self.load_image, args=(self.output_NDVI_aqua, "SP", self.verbose))
            terraRS.start()
            aquaRS.start()
            terraSP.start()
            aquaSP.start()
            #self.load_image(self.output_NDVI_aqua, "SP", self.verbose)
