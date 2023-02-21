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
## JPEGS are stored in the '_Reduced_Images_v#'.
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
# import a groupby() method
# from itertools module
from itertools import groupby
#metadata lib
import sys
import csv
from datetime import datetime
import shutil
import re
import arcpy
from arcpy import metadata as md
arcpy.env.parallelProcessingFactor = "100%"
    
# Set local variables
liste_fichiers=[]
log=[]
image_folder = arcpy.GetParameterAsText(0)
out_folder_path = arcpy.GetParameterAsText(1)
metadatafile = arcpy.GetParameterAsText(2)
georeference_checked=arcpy.GetParameterAsText(3)
georeference_file = arcpy.GetParameterAsText(4)
path_field = arcpy.GetParameterAsText(5)
flt_dir_field = arcpy.GetParameterAsText(6)
scale_dir_field = arcpy.GetParameterAsText(7)
    
#head of log file
head=['index','source file location','source file size','new file location','new file size','mosaic dataset name','output coordinate system','start','end','duration','title','tags','summary','description','credits','Use limitations','extent','scale range','status','error detail']
log.append(head)
#check if a field exist in a giving SHP
def checkFieldinSHP(shp,path_field,flt_dir_field,scale_dir_field):
    res=''
    desc = arcpy.Describe(shp)
    flds = desc.fields
    missingField=''
    
    listFields=[]
    
    for fld in flds:
        listFields.append(fld.name)
        
            
    if path_field not in listFields:
        res='Missing path Column'
    
    if flt_dir_field not in listFields:
        res=res+' Missing flt_dir Column'
    if scale_dir_field not in listFields:
        res=res+' Missing scale Column'
        
    return res
    
    
#georeference a raster file by generating a world file from a shp,
def georeference(Target_shapefile,raster_file,path_field,flt_dir_field,scale_dir_field):
    log=''
    
        
    raster_name=raster_file[raster_file.rfind('/')+1:]
    raster_name=raster_name[:raster_name.rfind('.')]
    
    if os.path.exists(Target_shapefile):
        res=checkFieldinSHP(Target_shapefile,path_field,flt_dir_field,scale_dir_field)  
        
        if res=='':
            
           
            Output_location= raster_file[:raster_file.rfind('/')]
            fields = [path_field, flt_dir_field,scale_dir_field, 'SHAPE@X', 'SHAPE@Y']
            cursor = arcpy.da.SearchCursor(Target_shapefile, fields)
            found=False
            
            for row in cursor:
                PATH, FL_DIR, SCALE, LONG, LAT = [cursor[i] for i in (0, 1, 2, 3, 4)]
                
                if PATH is not None and str(PATH)!='':
                     
                    if raster_name in PATH :
                    
                        found=True
                        if FL_DIR is not None and str(FL_DIR)!='':
                         
                            #First set of calculations handles North-South flightline orientations             
                            if FL_DIR == 'NS':
                                if str(SCALE) == '10000':
                                    # optimized for northern Utah
                                    longitude = LONG - 1600
                                    latitude = LAT + 1600
                                    f = open(Output_location + '/' + raster_name + '.tfw', 'w')
                                    f.write('0.172000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('-0.172000000000000000\n')
                                    f.write(repr(longitude) + "\n")
                                    f.write(repr(latitude) + "\n")
                                    f.close()
                                elif str(SCALE) == '20000':
                                    # optimized for western Ohio
                                    longitude = LONG - 3050
                                    latitude = LAT + 3050
                                    f = open(Output_location + '/' + raster_name + '.tfw', 'w')
                                    f.write('0.337000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('-0.337000000000000000\n')
                                    f.write(repr(longitude) + "\n")
                                    f.write(repr(latitude) + "\n")
                                    f.close()
                                elif str(SCALE) == '40000':
                                    # optimized for central Utah
                                    longitude = LONG - 6000
                                    latitude = LAT + 6000
                                    f = open(Output_location + '/' + raster_name + '.tfw', 'w')
                                    f.write('0.63000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('-0.630000000000000000\n')
                                    f.write(repr(longitude) + "\n")
                                    f.write(repr(latitude) + "\n")
                                    f.close()
                                elif str(SCALE) == '60000':
                                    # NHAP scans have instrument strip in top of scan that is accounted for.
                                    # The numbers shown here to create the tfw are manupulated to force
                                    # the creation of usable world files.
                                    # Optimized for West Virginia
                                    longitude = LONG - 9900
                                    latitude = LAT + 10500
                                    f = open(Output_location +  '/' + raster_name + '.tfw', 'w')
                                    f.write('1.010000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('0.000000000000000000\n')
                                    f.write('-1.010000000000000000\n')
                                    f.write(repr(longitude) + "\n")
                                    f.write(repr(latitude) + "\n")
                                    f.close()
                               
                                else:
                                    log=raster_name + " SHP is missing str(SCALE) information and cannot be rendered."
                            elif FL_DIR == 'EW':
                            
                                if str(SCALE) == '10000':
                                    # optimized for northern Utah
                                    longitude = LONG - 1600
                                    latitude = LAT + 1600
                                    f = open(Output_location +  '/' + raster_name + '.tfw', 'w')
                                    f.write('0.000000000000000000\n')
                                    f.write('0.172000000000000000\n')
                                    f.write('0.172000000000000000\\n')
                                    f.write('-0.000000000000000000\n')
                                    f.write(repr(longitude) + "\n")
                                    f.write(repr(latitude) + "\n")
                                    f.close()
                                    
                                elif str(SCALE) == '20000':
                                    # This one only works for east-west flightline county projects
                                    # optimized for western Ohio
                                        longitude = LONG - 3050
                                        latitude = LAT - 3050
                                        f = open(Output_location +  '/' + raster_name + '.tfw', 'w')
                                        f.write('0.000000000000000000\n')
                                        f.write('0.337000000000000000\n')
                                        f.write('0.337000000000000000\n')
                                        f.write('-0.000000000000000000\n')
                                        f.write(repr(longitude) + "\n")
                                        f.write(repr(latitude) + "\n")
                                        f.close()
                        
                                elif str(SCALE) == '40000':
                                    # Only for north-south flightlines
                                    # optimized for central Utah
                                    longitude = LONG - 6000
                                    latitude = LAT + 6000
                                    f = open(Output_location +  '/' + raster_name + '.tfw', 'w')
                                    f.write('0.00000000000000000\n')
                                    f.write('0.630000000000000000\n')
                                    f.write('0.630000000000000000\n')
                                    f.write('-0.000000000000000000\n')
                                    f.write(repr(longitude) + "\n")
                                    f.write(repr(latitude) + "\n")
                                    f.close()
                                else:
                                    log=raster_name + " SHP is missing scale information, and a world file could not be created."
                            
                            else:
                                log=raster_name + " SHP does not have a standard FLT_DIR attribute, and a world file could not be created."
                                
                            break
                        else:
                            log="Referencing Info found but empty FLT_DIR" 
                            break
            if not found:
                    log="No referencing Info for this image in the SHP"
        else :
            log=res
        
    return log
def replace_txt(stringg):
    stringg=stringg.replace('<DIV STYLE="text-align:Left;"><DIV><P><SPAN>','').replace('<DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>','').replace('</SPAN></P></DIV></DIV>','').replace('</DIV>','')
    return stringg
    
def getIndexNewFolder(image_folder):
    #Root Name of the input images folder
    rootName=image_folder[image_folder.rfind('\\')+1:]
    list_Reduced_folders=[]
    image_folder=image_folder[:image_folder.rfind('\\')]
    
    for elem in os.listdir(image_folder) :
        if  os.path.isdir(image_folder+'\\'+elem):
            if rootName+'_Reduced_Images_v' in elem :
                list_Reduced_folders.append(elem)
    
    listIndexes=[]
    
    
    for folder in list_Reduced_folders :
        match=re.findall('\d+',folder)
        
        if len(match)>0:
            if match[0].isdigit():
                listIndexes.append(int(match[0]))
    max_index=0
        
    if len(listIndexes)!=0 :
        max_index=max(listIndexes)+1
    
    return rootName+'_Reduced_Images_v'+str(max_index)
reduced_image_folder=getIndexNewFolder(image_folder)    
    
def reducedPathCreate(image_path,reducedFolderName):
    #export raster to tiff format
    dir1=image_folder[:image_folder.rfind('\\')]
    image_dir=image_folder[image_folder.rfind('\\')+1:]
    imp=image_path
    imp=imp.replace('/','\\')
            
    image_name=imp[imp.rfind('\\')+1:]
    image_name=image_name[:image_name.rfind('.')]
            
    imp=imp[:imp.rfind('\\')]
   
    dir2=imp.replace(image_folder,'')
    dirf=reducedFolderName+dir2
    path = os.path.join(dir1,dirf)
    if not os.path.isdir(path):
        os.makedirs(path)
                
    newPathFile=path+'\\'+image_name+'.jpg'
    return newPathFile
def rasSize(raster):
    
    basename = os.path.basename(raster).split(".")[0]
    rootFolder = os.path.dirname(raster)
    associatedFiles = [os.path.join(rootFolder,f) for f in next(os.walk(os.path.dirname(raster)))[2] if f.split(".")[0] == basename]
    if len(os.path.basename(raster).split(".")) == 1:
        fileList = next(os.walk(raster))[2]
        dirSize = sum([os.path.getsize(os.path.join(raster,f)) for f in fileList])
        rasSize = sum([os.path.getsize(f) for f in associatedFiles]) + dirSize
    else:
        rasSize = sum([os.path.getsize(f) for f in associatedFiles])
    
    return rasSize
def convertSize(size,precision=2):
    
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    return "%.*f %s"%(precision,size,suffixes[suffixIndex])
def listerFichier(path):
            listefichiers = listdir(path)
            if listefichiers != None:
                for f in listefichiers :
                    if(isfile(path+"/"+f)):
                        liste_fichiers.append(path+"/"+f)
                    elif(isdir(path+"/"+f)):
                        temp = listerFichier(path+"/"+f)
            return liste_fichiers
def readMetadataFile(file):
    list_of_csv=[]
    try:
        with open(file, 'r') as read_obj:
      
            # Return a reader object which will
            # iterate over lines in the given csvfile
            csv_reader = csv.reader(read_obj)
            # convert string to list
            list_of_csv = list(csv_reader)
    except:
        pass
    return list_of_csv
def getMetadataRaster(file,listFiles):
    listFiles=listFiles[1:]
    for f in listFiles:
        x=f[0].split(';')
        if x[1]==file:
            return x
    return []
#Read metadatafile in a List
list_noMetadataFile=readMetadataFile(metadatafile)
def addLog(index,filePath,newPathFile,mosaicName,crs,start,end,state,errorDetail):
    logRow=[]
    logRow.append(index)
    logRow.append(filePath)
    logRow.append(convertSize(rasSize(filePath)))
    logRow.append(newPathFile)
    logRow.append(convertSize(rasSize(newPathFile)))
    logRow.append(mosaicName)
    logRow.append(crs)
    logRow.append(start.replace('Start Time: ',''))
    end1=end.replace('Succeeded at ','')
    logRow.append(end1[:end1.find('(')])
    #extract duration
    dur=end[end.find('(')+1:]
    dur=dur.replace(',','.')
    dur=re.findall('\d+.\d+',dur)
    if len(dur)==1:
        logRow.append(str(dur[0])+' sec')
    else:
        logRow.append('0 sec')
        
    #raster metadata
    raster = arcpy.Raster(filePath)
    item_md = md.Metadata(raster)
    if item_md.title is not None :
        logRow.append(replace_txt(item_md.title))
    else :
        logRow.append('')
        
    if item_md.tags is not None :
        logRow.append(replace_txt(item_md.tags))
    else :
        logRow.append('')
        
    if item_md.summary is not None :
        logRow.append(replace_txt(item_md.summary))
    else :
        logRow.append('')
        
    if item_md.description is not None :
        logRow.append(replace_txt(item_md.description))
    else :
        logRow.append('')
        
    if item_md.credits is not None :
        logRow.append(replace_txt(item_md.credits))
    else :
        logRow.append('')
        
    if item_md.accessConstraints is not None :
        logRow.append(replace_txt(item_md.accessConstraints))
    else :
        logRow.append('')
    
    logRow.append(raster.extent)
    logRow.append(str(item_md.minScale) +'-'+str(item_md.maxScale))
    logRow.append(state)
    logRow.append(errorDetail)
    log.append(logRow)
# define a function for key
def key_func(k):
    return k['crs']
 
def copyFromToReduce(fromPath,toPath):
    arcpy.management.CopyRaster(fromPath,toPath, '', None, "256", "NONE", "NONE", "8_BIT_UNSIGNED", "NONE", "NONE", "JPEG", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
def edit_define_metadata(file,listMetadata):
    
    # Create a new Metadata object and add some content to it
    new_md = md.Metadata()
    new_md.title = listMetadata[0]
    new_md.tags = listMetadata[1]
    new_md.summary = listMetadata[2]
    new_md.description = listMetadata[3]
    new_md.credits = listMetadata[4]
    new_md.accessConstraints = listMetadata[5]
    raster = arcpy.Raster(file)
    extent=raster.extent
    new_md.extent = str(extent)
    # Assign the Metadata object's content to a target item
    tgt_item_md = md.Metadata(file)
    if not tgt_item_md.isReadOnly:
        tgt_item_md.copy(new_md)
        tgt_item_md.save()
        
def returnImages(path):
        liste_fichiers.clear()
        liste_images=[]
        files_list = []
        files_list = listerFichier(path)
        listFormats=['jpg','tif','png','jp2','img','bmp','gif','crf','bip']
        index=1
        
        for f in files_list:
            logRow=[]
            if f[-3:] in listFormats or  f[-4:] in listFormats or  f[-6:] in listFormats:
                try :
                    
                    crs = arcpy.Describe (f).spatialReference.name
                    
                    if crs!='Unknown' :
                        
                        dict={'file': f,'crs': crs}
                        liste_images.append(dict)
                        index=index+1
                    #if the image is unreferenced generated its world file, if shp exists    
                    else:
                        if georeference_checked=='true':
                        
                            res=georeference(georeference_file,f,path_field,flt_dir_field,scale_dir_field)
                            
                            if res=='':
                                #define projection for the raster file
                                sr = arcpy.SpatialReference(3857)
                                arcpy.DefineProjection_management(f, sr)
                                    
                                dict={'file': f,'crs': 'WGS 1984 Web Mercator (auxiliary sphere)'}
                                liste_images.append(dict)
                                index=index+1
                            else:
                                newPathFile=reducedPathCreate(f,reduced_image_folder)
                                #copy the raster from  the source path to the new reduced images location
                                copyFromToReduce(f,newPathFile)
                                metadata_list=getMetadataRaster(f,list_noMetadataFile)
                                #if the file is in the csv file edit it the metadata of the source and newly created image
                                if len(metadata_list)>=2:
                                    metadata_list=metadata_list[2:]
                                    edit_define_metadata(f,metadata_list)
                                    edit_define_metadata(newPathFile,metadata_list)
                                
                                addLog(index,f,newPathFile,'','Unknown','','','FAILED',res)
                                index=index+1
                        else:
                                newPathFile=reducedPathCreate(f,reduced_image_folder)
                                copyFromToReduce(f,newPathFile)
                                addLog(index,f,newPathFile,'','Unknown','','','FAILED','Downsized but not georeferenced')
                                index=index+1
                               
                except Exception:
                    
                    e = sys.exc_info()[1]
                    addLog(index,f,'','','Unknown','','','FAILED',e.args[0])
                    
                    index=index+1
                    arcpy.AddError(e.args[0])
                    continue
        return liste_images
    
#List of images in the giving folder
list_images=returnImages(image_folder)
# sort INFO data by 'company' key.
list_images = sorted(list_images, key=key_func)
arcpy.env.workspace = out_folder_path
# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d%m%Y_%Hh%Mmin%S")
#Root Name of the input images folder
rootName=image_folder[image_folder.rfind('\\')+1:]
#FileGDB Name
gdbname = rootName+"_"+dt_string+".gdb"
index=len(log)
if len(list_images)>0:
    # Execute CreateFileGDB
    arcpy.CreateFileGDB_management(out_folder_path, gdbname)
    for key, value in groupby(list_images, key_func):
        mcName=key.replace('(','_').replace(')','_').replace(' ','_')
        mdname = "MosaicDataset_"+mcName
        list_dic_im=list(value)
        crs = arcpy.Describe (list_dic_im[0]['file']).spatialReference
        noband = "3"
        pixtype = "8_BIT_UNSIGNED"
        pdef = "NONE"
        wavelength = ""
        nb_images='_'+str(len(list_dic_im))+'images'
        arcpy.AddMessage(crs.name)
        arcpy.CreateMosaicDataset_management(gdbname, mdname+nb_images, crs, noband,pixtype, pdef, wavelength)
        
        for imPath in list_dic_im :
            logRow=[]
            
            try :
                newPathFile=reducedPathCreate(imPath['file'],reduced_image_folder)
                #copy the raster from  the source path to the new reduced images location
                copyFromToReduce(imPath['file'],newPathFile)
                if len(list_noMetadataFile)!=0:
                    
                    metadata_list=getMetadataRaster(imPath['file'],list_noMetadataFile)
                    #if the file is in the csv file edit it the metadata of the source and newly created image
                    if len(metadata_list)>=2:
                        metadata_list=metadata_list[2:]
                        edit_define_metadata(imPath['file'],metadata_list)
                        edit_define_metadata(newPathFile,metadata_list)
                #add raster to mosaic
                arcpy.management.AddRastersToMosaicDataset(out_folder_path+'\\'+gdbname+'\\'+mdname+nb_images, "Raster Dataset", imPath['file'], "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "BUILD_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "ESTIMATE_STATISTICS", None, "NO_PIXEL_CACHE")
                #arcpy.management.AddRastersToMosaicDataset(r"D:\Ari\Bureau\Group Images GDB\tif_wo_j2w_07102022_22h50min23.gdb\MosaicDataset_WGS_1984_Web_Mercator__auxiliary_sphere__2images", "Raster Dataset", r"'D:\Ari\Bureau\Group Images GDB\tif_wo_j2w\000953_0144.tif'", "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, '', "SUBFOLDERS", "ALLOW_DUPLICATES", "BUILD_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", '', "NO_FORCE_SPATIAL_REFERENCE", "ESTIMATE_STATISTICS", None, "NO_PIXEL_CACHE", r"C:\Users\user\AppData\Local\ESRI\rasterproxies\MosaicDataset_WGS_1984_Web_Mercator__auxiliary_sphere__2images")
                message_count = arcpy.GetMessageCount()
                start=arcpy.GetMessage(0)
                end=arcpy.GetMessage(message_count - 1)
                
                addLog(index,imPath['file'],newPathFile,mdname,crs.name,start,end,'SUCCESS','')
                arcpy.AddMessage(imPath['file'])
                index=index+1
                
            except Exception:
                
                e = sys.exc_info()[1]
                addLog(index,imPath['file'],'','',crs.name,'','','FAILED',e.args[0])
               
                arcpy.AddError(e.args[0])
                
                index=index+1
                
                continue
     
# datetime object containing current date and time
now = datetime.now()
dt_string = now.strftime("%d%m%Y_%Hh%Mmin%S")
with open(out_folder_path+"/log_"+dt_string+".csv","w", newline="") as f:
        writer = csv.writer(f,delimiter = "|")
        writer.writerows(log)
