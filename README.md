# ImagesLoader2Jpeg
 ArcPro Toolbox for downsizing .tif to .jpg, creating metadata, and tracking raster images.


# <a name="team-members"></a>Team Members
* "Arielle Simmons-Steffen" <arielle.simmons-steffen@usda.gov>
	- SRIC Illinois
	
## Project Summary
***
 
This script/toolbox (ArcPro - Python 3) assists in the organization, downsizing, and propagation of metadata for image files. 

As of 02/21/2022, there are 2 component files of the ImagesLoaderV5.tbx.

1) ImagesLoader
2) NoMetadataImagesList


## Parameters
***

1) ImagesLoader

This script creates a new directory of 'smaller' jpeg images (WITH Metadata) from an existing directory of images. It also creates a mosaic file that 
groups all the jpeg images together - and a tracking log (csv) file.

The folder of the smaller images is projected in the source projection (note: there is special handling for  cases with no known projection) 
AND are located in the same directory as the source images (in a folder with the source name concatenated with '_Reduced_Images_v#' at the end.

You MUST before running the ImagesLoader do 2 things:

1) use 'NoMetadataImagesList' to create a metadata csv file to be loaded into the reduced images that are in the '_Reduced_Images_v#'.

2) Set the Map Projection to the source data projection OR to 'EPSG: 3857' Meters if the source data is unprojected.


In the toolbox the user is given an option to 'Georeference non-Projected Images' this was designed for handling APFO imagery that should have a 
shapefile that contains the centerpoint location of the images. These images are all set to 

WGS 1984 Web Mercator (auxiliary sphere) and the Units to Meters.

The shapefile must contain an attribute which has the file path. Also the code is expecting a field designating the 'Flight Direction' and image 'Scale'.


2) NoMetadataImagesList

This script creates a csv file template for creating metadata for the smaller images. You are required to run this script BEFORE
running 'ImagesLoader'. Input is a directory of source images & an output location.

## Change log
***

10/10/2022 - Initial Checkin


![Screenshot](https://github.com/IL-NRCS/ImagesLoader/blob/main/Capture.JPG)

