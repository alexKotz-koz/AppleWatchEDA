import xml.etree.ElementTree as ET
import json
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import time
from statistical_tests import StatisticalTest
import os

# Desc: Extracts data for each of the data types passed to the function
# Input: Dictionary containing data type specific information used in extraction process
# Output: A JSON and a CSV file that contains all of the extracted data for the specified data type and year
def data_extract(object):
    # get root from object 
    root = object["root"]
    # get date and time variables from the data type object
    dataTypeString = object["dataTypeString"]
    year = object["year"]
    objectParameters = object["objectParameters"]
    # create output file name string
    outputFileName = object["outputFileName"]

    data = {}
    # helper function used for flattening data
    def data_extract_helper(data, dict_func):
        return [
            dict_func(date, obs)
            for date, observations in data.items()
            for obs in observations
        ]

    # iterate through each observation ("Record") in the exported data
    for child in root:
        if child.tag == "Record":
            # extract date/times (measurement creation date, the start date/time of the measurement, and the end date/time of the observantion)
            creationDate = child.attrib.get("creationDate")[:-15]
            creationDateTime = child.attrib.get("creationDate")[11:19]
            startDate = child.attrib.get("startDate")[:-15]
            startTime = child.attrib.get("startDate")[11:19]
            endDate = child.attrib.get("endDate")[:-15]
            endTime = child.attrib.get("endDate")[11:19]

            # calculate the total time the measurement took
            startTimeFormatted = datetime.strptime(startTime, "%H:%M:%S")
            endTimeFormatted = datetime.strptime(endTime, "%H:%M:%S")
            totalTime = str(endTimeFormatted - startTimeFormatted)


            # refactor, not all types will use/ have sourceName

            # extract the device name and type, where the measurement was taken
            source = child.attrib.get("sourceName")
            if "iPhone" in source:
                source = "iPhone"
            elif "Watch" in source:
                source = "Watch"
            else:
                source = "Other"

            device = child.attrib.get("device")
            if device != None:
                start = device.find("name:") + len("name:")
                end = device.find(",", start)
                device = device[start:end].strip()

            # extract the unit from the measurement observation
            unit = child.attrib.get("unit") or ""

            # if the record is the same type as the object passed and the year matches the object defined year, add the following to the output json object:
            if child.attrib.get("type") == dataTypeString and creationDate[0:4] == year:
                args = (child, creationDateTime)
                if "startTime" != None:
                    args += (startTime,)
                if "endTime" != None:
                    args += (endTime,)
                if "totalTime" != None:
                    args += (totalTime,)
                if "source" != None:
                    args += (source,)
                if "unit" != None:
                    args += (unit,)
                if "device" != None:
                    args += (device,)

                # concatinate the arguments from above into a single object
                objectParameters = object["objectParameters"](*args)

                # if the creation date is a key in the output object, add the objectParameters object to that key-value pair, 
                # else create an item in the output object where the creation date is the key and the value contains the objectParameters object
                if creationDate in data.keys():
                    data[creationDate].append(objectParameters)
                else:
                    data[creationDate] = [objectParameters]


    if not os.path.exists("../data/json"):
        os.makedirs("../data/json")
    if not os.path.exists("../data/csv"):
        os.makedirs("../data/csv")

    outputFileJSON = "../data/json/" +outputFileName + ".json"
    with open(outputFileJSON, "w") as file:
        json.dump(data, file)

    # flatten data observations per date
    flatData = data_extract_helper(data, lambda date, obs: {
        'date': date,
        **obs
    })

    df = pd.DataFrame(flatData)
    outputFileCSV = "../data/csv/" + outputFileName + ".csv"
    df.to_csv(outputFileCSV)

# Desc: Creates a file that contains a subset of the original data type file (three days worth of data)
# Input: Data type specific file, generated from data_extract()
# Output: File containing a subset of the original file (first three days of data, unless specified by the optional days argument)
def three_days_data(file, days=None):
    data = []
    firstThreeDates = []
    outputData = []
    header = ""
    # open file and extract each line into a sub list of data
    with open(file, "r") as file:
        header = file.readline()
        for observation in file:
            data.append(observation)
    
    if days == None:
        # extract the first three dates from the file
        for observation in data:
            observation = observation.split(",")
            if len(firstThreeDates) >= 3:
                break
            else:
                if observation[1] not in firstThreeDates:
                    firstThreeDates.append(observation[1])
    else:
        firstThreeDates = days

    # remove the first item from the firstThreeDates -- can refactor
    if 'date' in firstThreeDates:
        firstThreeDates.remove('date')

    # extract the observations that occur on the firstThreeDates
    for observation in data:
        observation = observation.split(",")
        if observation[1] in firstThreeDates:
            outputData.append(observation)

    # remove newline character from any data point in each observation
    for obs in outputData:
        for index, item in enumerate(obs):
            if '\n' in item:
                obs[index] = item.replace('\n','')
    
    # clean header
    header = header.split(',')
    for index,item in enumerate(header):
        if '\n' in item:
            header[index] = item.replace('\n', '') 

    outputDf = pd.DataFrame(outputData, columns=header)
    dir, fileName = os.path.split(file.name)
    outputfilename= "three_days_" + fileName
    outputfilepath = os.path.join(dir, outputfilename)
    
    outputDf.to_csv(outputfilepath)
    return firstThreeDates



# Ouput/Desc: txt file that contains a list of all available data types from health app export.xml
def extract_data_types(root):
    dataTypes = []
    uniqueTypes = []
    # iterate thru each record in export.xml
    for child in root:
        if child.tag == "Record":
            # if the datatype name is not already in the uniqueTypes list, append it
            if child.attrib.get("type") not in uniqueTypes:
                uniqueTypes.append(child.attrib.get("type"))
    # strip off the apple prefix to get a clean datatype name
    for item in uniqueTypes:
        if "HKQuantityTypeIdentifier" in item:
            dataItem = item.replace("HKQuantityTypeIdentifier", "")
            if dataItem not in dataTypes:
                dataTypes.append(dataItem)
        elif "HKCategoryTypeIdentifier" in item:
            dataItem = item.replace("HKCategoryTypeIdentifier", "")
            if dataItem not in dataTypes:
                dataTypes.append(dataItem)
    # write the datatypes to a file
    with open("dataTypes.txt", "w") as file:
        for item in dataTypes:
            file.write(item + ", ")

# Desc: Static dictionaries for each data type
def static_data(root, year):
    # each dictionary has a unique set of key value pairs that are used to search for, and extract, the corresponding data from the export.xml file.
        # each dictionary specifies the name of the specific datatype output file
    heartRate = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierHeartRate",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None, device=None: {
            "heartRate": child.attrib.get("value"),
            "time": creationDateTime,
        },
        "outputFileName": "heart_rate_data",
    }
    restingHeartRate = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierRestingHeartRate",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None,
        device=None:{
            "heartRate": child.attrib.get("value"),
            "time": creationDateTime,
        },
        "outputFileName": "resting_heart_rate_data",
    }
    heartRateVariability = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None, device=None: {
            "heartRateVariability": child.attrib.get("value"),
            "time": creationDateTime,
        },
        "outputFileName": "heart_rate_variability_data",
    }
    steps = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierStepCount",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None, device=None: {
            "startTime": startTime,
            "endTime": endTime,
            "totalTime": str(totalTime),
            "steps": child.attrib.get("value"),
            "source": source,
        },
        "outputFileName": "steps_data",
    }
    walkingStepLength = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierWalkingStepLength",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None, device=None: {
            "startTime": startTime,
            "endTime": endTime,
            "totalTime": str(totalTime),
            "gaitLength": child.attrib.get("value"),
            "unit": unit,
            "source": source,
        },
        "outputFileName": "gait_length_data"
    }
    envAudioExposure = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierEnvironmentalAudioExposure",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None, device=None: {
            "startTime": startTime,
            "endTime": endTime,
            "totalTime": str(totalTime),
            "environmentalAudioExposure": child.attrib.get("value"),
            "unit": child.attrib.get("unit"),
            "device": device,
        },
        "outputFileName": "environmental_audio_exposure_data",
    }
    headphoneAudioExposure = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierHeadphoneAudioExposure",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None, device=None: {
            "startTime": startTime,
            "endTime": endTime,
            "totalTime": str(totalTime),
            "headphoneAudioExposure": child.attrib.get("value"),
            "unit": child.attrib.get("unit"),
            "device": device,
        },
        "outputFileName": "headphone_audio_exposure_data",
    }
    timeInDaylight = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierTimeInDaylight",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None, device=None: {
            "startTime": startTime,
            "endTime": endTime,
            "totalTime": str(totalTime),
            "timeInDayLightValue": child.attrib.get("value"),
            "unit": unit,
        },
        "outputFileName": "time_in_daylight_data",
    }
    spo2 = {
        "root": root,
        "dataTypeString": "HKQuantityTypeIdentifierOxygenSaturation",
        "year": year,
        "objectParameters": lambda child, creationDateTime, startTime=None, endTime=None, totalTime=None, source=None, unit=None,
        device=None: {
            "startTime": startTime,
            "endTime": endTime,
            "totalTime": totalTime,
            "SpO2": child.attrib.get("value"),
            "source": source,
            "unit": unit,
        },
        "outputFileName": "spo2_data"
    }

    return heartRate, restingHeartRate, heartRateVariability, steps, walkingStepLength, envAudioExposure, headphoneAudioExposure, timeInDaylight, spo2


def main():

    # get export.xml tree root
    tree = ET.parse("../../apple_health_export_data/apple_health_export/export.xml")
    root = tree.getroot()

    # To extract data from a different year please replace this with the desired year, format must be YYYY
    year = "2023"

    (
        heartRate, 
        restingHeartRate,
        heartRateVariability, 
        steps,
        walkingStepLength,
        envAudioExposure, 
        headphoneAudioExposure, 
        timeInDaylight,
        spo2
        ) = static_data(root, year)
    data_extract(heartRate)
    data_extract(restingHeartRate)
    data_extract(heartRateVariability)
    data_extract(steps)
    data_extract(walkingStepLength)
    data_extract(envAudioExposure)
    data_extract(headphoneAudioExposure)
    data_extract(timeInDaylight)
    data_extract(spo2)

    # get the first three dates available in the hear rate file and use as the dates to extract for the remaining files
    firstThreeDates = three_days_data("../data/csv/heart_rate_data.csv")
    three_days_data('../data/csv/steps_data.csv', firstThreeDates)
    three_days_data('../data/csv/spo2_data.csv',firstThreeDates)
    three_days_data('../data/csv/gait_length_data.csv',firstThreeDates)

    statisticalTestInstance = StatisticalTest(
            heartRateFile="../data/csv/three_days_heart_rate_data.csv", 
            stepsFile="../data/csv/three_days_steps_data.csv",
            gaitFile="../data/csv/three_days_gait_length_data.csv",
            spo2File="../data/csv/three_days_spo2_data.csv"
        )

    statisticalTestInstance.descriptive_statistics()

    # uncomment if you would like to create a file to see all available data types in
    # extract_data_types(root)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"Runtime: {end-start}")
