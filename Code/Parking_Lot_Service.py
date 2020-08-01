"""
Created on Thu Jul 30 14:19:30 2020

@author: Tal Cohen

Description: Parking lot service
"""

# Import libraries
import cv2
import numpy as np
import requests
import io
import json  
import sys
from datetime import datetime
from pymongo import MongoClient

# Recursive function to sum the digits of a given number
def sumOfDigits(n):
    if n < 10:
        return n 
    return n%10 + sumOfDigits(n//10)

# Check if a given number is divisible by 7
def isDivideBy7(n):
    if n%7 == 0:
        return True

# Function for process the plate image before pass to the OCR
def preProccessing(img_file):
    license_plate_image = cv2.imread(img_file)
    
    # Check if the image is too small for the precess
    height, width, _ = license_plate_image.shape
    if height*width < 1600:
        print("The image of the plate is too small, Please get closer.")
        sys.exit(0)
        
    license_plate_image_resized = cv2.resize(license_plate_image, (400,100), cv2.INTER_AREA)
    license_plate_image_gray = cv2.cvtColor(license_plate_image_resized, cv2.COLOR_BGR2GRAY)
    license_plate_image_thresh = cv2.adaptiveThreshold(license_plate_image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, 9)
    kernel = np.ones((5,5), np.uint8)
    license_plate_image_proccesed = cv2.morphologyEx(license_plate_image_thresh, cv2.MORPH_OPEN, kernel)
    return [license_plate_image_proccesed, license_plate_image_resized]

# Function to apply the OCR on the plate image
def applyOCR(license_plate_image, img_file):
    # OCR
    url_api = "https://api.ocr.space/parse/image"

    # We must send the image as bytes and compressed because we have 1MB in the free version
    _, compressed_image = cv2.imencode('.png', license_plate_image, [1, 90])
    file_bytes = io.BytesIO(compressed_image)

    print("sending request to OCR.space")
    
    # Apply the OCR.space on a compressed binary image 
    result = requests.post(url_api, 
                           files = {img_file: file_bytes},
                           data = {'apikey': 'cd0de8a2a988957',
                                   'scale': True,
                                   'OCREngine': 2})
    
    result = result.content.decode()
    result = json.loads(result)
    return result

# Function that remove punctuation and arrange
# the variable of the detected text from the OCR
def arrangeDetectedPlateNumber(detected_text):
    # Remove punctuation loop
    plate_number_list = list()
    for letter in detected_text:
        if letter.isdigit() or letter.isalpha():
            plate_number_list.append(letter)

    # Return a string with only relevant characters
    return ''.join(plate_number_list)

def isAuthorized(plate_number):
    number_of_digits = len(plate_number)
    prohibited_numbers = ['85', '86', '87', '88', '89', '00']
    public_transportation_numbers = ['25', '26']
    
    # Conditions if this license plate number authorized or prohibited
    if  any(letter.isalpha() for letter in plate_number[:number_of_digits-1]):
        print("The license plate was read incorrectly.\nPlease get another image.")
        sys.exit(0)
        
    elif number_of_digits < 6 and number_of_digits > 8:
        print("Error! invalid number of digits in the license plate.\nPlease get another image.")
        sys_exit(0)
        
    elif any(letter.isalpha() for letter in plate_number):
        print("Military and law enforcement vehicles are prohibited")
        is_authorized = False
        rejection_reason = 'law_enforcement'
        
    elif plate_number[(number_of_digits-2):] in public_transportation_numbers:
        print("Public transportation vehicles are prohibited")
        is_authorized = False
        rejection_reason = 'public_transportation'
    
    elif number_of_digits == 7 and plate_number[(number_of_digits-2):] in prohibited_numbers:
        print("Prohibited license plate number")
        is_authorized = False
        rejection_reason = 'prohibited_number_plates'
    
    elif number_of_digits in [7, 8] and isDivideBy7(sumOfDigits(int(plate_number))):
        print("Suspected as operated by gas, therefore are prohibited")
        is_authorized = False
        rejection_reason = 'divide_by_7'
    
    else:
        print("Authorized to enter to the parking lot")
        is_authorized = True
        rejection_reason = 'passed_in'
        
    return [is_authorized, rejection_reason]
    
def insertInfo(plate_number, decision_flag, rejection_reason):
    record = {"Plate Number": plate_number,
              "Decision": decision_flag,
              "Reason": rejection_reason,
              "Entry Time": datetime.now().replace(microsecond=0)
              }
    information.insert_one(record)

# Image File
img_file = '13.png'

# Create my database with Mongo
mongo_client = MongoClient('localhost', 27017)
mydb = mongo_client['Parking-Lot']
information = mydb.parking_lot_info

# Get the proccesed image of the license plate
license_plate_image, original_image = preProccessing(img_file)

print("finished pre processing")

# Get the result of the OCR.space from the function
result_of_OCR = applyOCR(license_plate_image, img_file)

print("finished pre OCR detection")

try:
    detected_text = result_of_OCR.get('ParsedResults')[0].get('ParsedText')
except:
    print("There is an Error during the process, Please get another image.", sys.exc_info()[0])
    sys.exit(0)

# Arranges the number
plate_number = arrangeDetectedPlateNumber(detected_text)

# Get information about authorization and the reason
is_authorized, rejection_reason = isAuthorized(plate_number)

# Add new information to the mongo database
insertInfo(plate_number, str(is_authorized), rejection_reason)

print("Plate Number: ", plate_number)

#cv2.imshow("License plate image", original_image)
#cv2.waitKey(0)