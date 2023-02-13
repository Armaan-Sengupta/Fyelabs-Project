import laspy
import open3d as o3d
import numpy as np

"""
By: Armaan Sengupta
Date: 2023-02-12
Fyelabs LIDAR Project

Attempt at question 11a
"""


DEBUG=True
dirtyFile = None


def debug(var):
    if DEBUG:
        print(var)


def cleanFile(filename, classificationToKeep):
    #read file
    dirtyFile = laspy.read(filename+".las")



    if classificationToKeep not in np.unique(dirtyFile.classification):
        print("No points to filter")
        exit()



    #Filtering all the points that are not classified (AKA all the high points in the sky)

    buildings = laspy.create(point_format=dirtyFile.header.point_format, file_version=dirtyFile.header.version)
    buildings.points = dirtyFile.points[dirtyFile.classification == classificationToKeep]
    NEW_FILE_NAME = f"CaliforniaBuildingsOnly.las"

    buildings.write(NEW_FILE_NAME) 

    return NEW_FILE_NAME


def checkIfCleaned(filename, classificationToRemove):
    cleanedFile = laspy.read(filename)

    if classificationToRemove in np.unique(cleanedFile.classification):
        print("Error: File not cleaned")

    else:
        print("File cleaned")


def main():
    FILENAME=input("Enter file name: ")
    CLASSIFICATION_TO_REMOVE = int(input("Enter classification to remove: "))

    cleanedFile = cleanFile(FILENAME, CLASSIFICATION_TO_REMOVE)
    checkIfCleaned(cleanedFile, CLASSIFICATION_TO_REMOVE)
    print("Done!")


if __name__ == "__main__":
    main()