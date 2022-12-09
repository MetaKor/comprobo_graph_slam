import numpy as np
import cv2 as cv
from sklearn.cluster import KMeans
from collections import Counter
from objectclass import objectdetect
import os
from os import listdir
import inspect, os.path
import re

#TODO - Load all objects from folder
# Initialize primary color of each object
# Search for each object in video stream and determine if object is in frame
# If object is in frame, find the centroid and then


class objecttrack():
    def __init__(self, folder_name):
        # store the name of the folder where the object images are stored
        self.folder_name = folder_name
        # create a placeholder to store the tracking objects
        self.objects = None

    def load_objects(self):

        # find the current working directory
        path = os.getcwd() + "/" + self.folder_name

        object_list = []

        for objects in os.listdir(path):

            # the diameter of the image needs to be in the file name ex. greenball_5
            diameter = re.findall("(?<=_).+(?=\.)", objects)[0]

            # attempt to convert the number
            try:
                diameter = float(diameter)
            except NameError:
                print("Object Image Name has no Diameter ending, proper ex. greenball_5")

            # load the BGR image
            img = cv.imread(path + "/" + objects, cv.COLOR_BGR2HSV)

            # create an instance of the image
            landmark = objectdetect(img,diameter,objects)

            # find the primary color of the object
            landmark.find_color()

            # create the object class and append it to the list
            object_list.append(landmark)



        # Move the objects to a global placeholder
        self.objects = object_list

    def findcircles(self, image):
        # Apply a median blur to the image to reduce noise
        image = cv.medianBlur(image, 5)

        # find all of the circles in the image frame
        circles = cv.HoughCircles(image, cv.HOUGH_GRADIENT, 1, 20)

        # circles is a list of circle objects
        return circles

    def matchobjects(self, image, circles, tolerance):
        # identify if any of the circles are a known object in the user defined folder

        for circle in circles:
            # find if the center color of the circle matches any of the colors
            # note that images are [y,x,c] format
            circle_color = image[circle[1], circle[0]]

            # now assess if this color is within the tolerance range of any of the object colors
            for obj in self.objects:
                lower_range = [value * (1 - (tolerance/100)) for value in obj.primary_color]
                upper_range = [value * (1 - (tolerance/100)) for value in obj.primary_color]

                # find if the circle color is in the range of the color
                # zip creates a list of tuples
                lower_test = [True if x > y else False for x,y in zip(circle_color, lower_range)]
                upper_test = [True if x < y else False for x,y in zip(circle_color, upper_range)]

                # if any colors fall out of the range, move on
                if False in lower_test or False in upper_test:
                    continue
                else:
                    print(f"Matched object {obj.name}")



if __name__ == '__main__':

    tracker = objecttrack("trackingobjects")
    tracker.load_objects()

    # define where to receive the video stream
    cap = cv.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        # load the live video feed
        ret, frame = cap.read()
        if frame is None:
            continue

        # convert the video frame to HSV
        live_image = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        # also convert it to grey scale for Hough transformations
        grey_image = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # find the circles
        circles = tracker.findcircles(grey_image)

        if circles is not None and len(circles) > 0:
            print("circle found!")
            # match the circles to objects
            tracker.matchobjects(live_image, circles, 5)


        # set the dimensions of the video frame
        frame = np.array(cv.resize(frame,
                                    (frame.shape[1]//1,
                                     frame.shape[0]//1)))
        cv.imshow('Video Feed', frame)
        # if the user presses esc, terminate the process
        cv.waitKey(27)
    cv.destroyAllWindows()