Parking Lot Service

Description
This project is a parking lot service. The user provide an already cropped image of a Israeli license plate and the program decide whether or not to enter the parking lot according to a number of conditions.
The information about the number plate, the decision made by the program, the reason and the timestamp written in local database (I chose to use MongoDB) 

Result
The first image is an unexpected result gives this number plate the authorization but is law enforcement number plate, and it is not allowed to enter. Image 1 in the Appendices.
Second image is an expected result of car that prohibited to enter to the parking lot and that’s what the decision of the program. Image 2 in the Appendices.

Installations
I use Spyder editor (Anaconda) with Python 3.6 version
Download and install MongoDB and MongoDB compass
Install libraries in python: OpenCV, requests, pymongo, json (built-in from python 2.6 version), numpy.

API Reference 
Register to OCR.space and get an APIKEY.
https://ocr.space/OCRAPI

Futures
There is several thinks I intend to add.
First, option for the user to select his file and upload it from outside.
Second, Expend the options of the image and give the opportunity to input full image of the car (like if it was connect to a video camera at the entrance to the parking lot) and the program will needs to detect the region of interest of the license plate and cropped it according to the bounding box.

Credits
Okay Dexter youtube channel for the MongoDB tutorials.
Pysource youtube channel for the OCR.space tutorial. 
TubeMint youtube channel for the setup tutorial about MongoDB.
