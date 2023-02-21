###############################################
## A Simmons-Steffen                         ##
##                                           ##
##                                           ##
## USDA-NRCS                                 ##
## Date created: Feb 21, 2023                ##
## Date modified:                            ##
###############################################

## This script creates a new directory of .jpg images
## from an existing directory of .tif images. It also creates a
## mosaic file that groups all the .jpg images together.
## 
## The folder of the smaller images is projected in the
## source projection (note: there is special handling for 
## cases with no known projection) AND are located in the same
## directory as the source images (in a folder with the source
## name concatenated with '_Reduced_Images_v#' at the end.
##  
## You MUST before running the toolbox do 2 things:
## 
## 1) use 'NoMetadataImagesList' to create a metadata csv file 
##    that will create metadata for the images.
## 
## 2) Set the Map Projection to the source data projection
##    or to 'EPSG: 3857' Meters if the source data is 
##    unprojected.
##
## This that are in the '_Reduced_Images_v#'.
##
## User is given an option to 'Georeference non-Projected Images' 
## this was designed for handling APFO imagery that should have a 
## shapefile that contains the centerpoint location of the 
## images. These images are all set to 
## WGS 1984 Web Mercator (auxiliary sphere) and the Units to Meters.
## The shapefile must contain an attribute which has the file path.
## Also the code is expecting a field designating the 'Flight 
## Direction' and image 'Scale'. All images with 'EW' in their
## 'Flight Direction' field will be rotated 90 deg counter-clockwise.
##

import os
from os.path import isfile, isdir
from os import listdir
import arcpy
# import a groupby() method
#metadata lib
from arcpy import metadata as md

import sys
import csv

from datetime import datetime


liste_fichiers=[]

image_folder = arcpy.GetParameterAsText(0)
# Set local variables
out_folder_path = arcpy.GetParameterAsText(1)




def listerFichier(path):

            listefichiers = listdir(path)

            if listefichiers != None:

                for f in listefichiers :
                    if(isfile(path+"/"+f)):
                        liste_fichiers.append(path+"/"+f)
                    elif(isdir(path+"/"+f)):
                        temp = listerFichier(path+"/"+f)

            return liste_fichiers


def replace_txt(stringg):

    stringg=stringg.replace('<DIV STYLE="text-align:Left;"><DIV><P><SPAN>','').replace('<DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>','').replace('</SPAN></P></DIV></DIV>','').replace('</DIV>','')
    return stringg
    
def returnImages(path):

        liste_fichiers.clear()
        liste_images=[]

        #head of log file
        head=['index','source file location','title','tags','summary','description','credits','Use limitations']
        liste_images.append(head)
        
        files_list = listerFichier(path)
        listFormats=['jpg','tif','png','jp2','img','bmp','gif','crf','bip']
        index=1
        
        for f in files_list:
            
            if f[-3:] in listFormats or  f[-4:] in listFormats or  f[-6:] in listFormats:

                try :
                    
                        arcpy.AddMessage(f)
                        
                        raster = arcpy.Raster(f)
                        item_md = md.Metadata(raster)

                        title=item_md.title
                        tags=item_md.tags
                        summary=item_md.summary
                        description=item_md.description
                        credits_=item_md.credits
                        accessConstraints=item_md.accessConstraints
                        
                        if str(title)=='None' or str(tags)=='None' or str(summary)=='None' or str(description)=='None' or str(credits_)=='None' or str(accessConstraints)=='None' or str(title)=='' or str(tags)=='' or str(summary)=='' or str(description)=='' or str(credits_)=='' or str(accessConstraints)=='':
                             
                            arcpy.AddMessage(str(liste_images))
                            tg=''
                            smmry=''
                            desc=''
                            crdts=''
                            accConst=''
                            ttle=''
                            
                            if str(title)!='None': 
                                ttle=replace_txt(str(title))
                                
                            if str(tags)!='None': 
                                tg=replace_txt(str(tags))
                                
                            if str(summary)!='None' :
                                smmry=replace_txt(str(summary))
                                
                            if str(description)!='None' :      
                                desc=replace_txt(str(description))
                                
                            if str(credits_)!='None':
                                crdts=replace_txt(str(credits_))
                                
                            if str(accessConstraints)!='None':
                                 accConst=replace_txt(str(accessConstraints))
                                
                            liste_images.append([index,f,ttle,tg,smmry,desc,crdts,accConst])
                            index=index+1
                    
                        
                except Exception:

                    e = sys.exc_info()[1]
                    arcpy.AddError(e.args[0])
                    continue

        return liste_images


liste_images=returnImages(image_folder)
 
# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d%m%Y_%Hh%Mmin%S")

with open(out_folder_path+"/NoMetadataImages_"+dt_string+".csv","w", newline="") as f:
    writer = csv.writer(f,delimiter = ";")
    writer.writerows(liste_images)    
