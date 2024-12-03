import numpy as np
import cv2

class Pupil(object):
    """This class detects the iris of an eye and estimates the position of the pupil"""

    def __init__(self,eye_frame, threshold):
        self.iris_frame=None
        self.threshold= threshold
        self.x= None
        self.y= None

        self.detect_iris(eye_frame)

    @staticmethod
    def image_processing(eye_frame, threshold):
        """Performs operations on the eye frame to isolate the iris

        Arguments:
            eye_frame(numpy.ndarray): Frame containing an eye and nothing else
            threshold (int): Threshold value used to binarize the eye frame

        Returns:
            A frame with a single element representing the iris
        """
        kernel=np.ones((3,3),np.uint8) #A 3x3 matrix of ones, used as a structural element in morphological operations
        new_frame=cv2.bilateralFilter(eye_frame, 10,15,15)  #bilateral filter to reduce noise while preserving edges. The parameters control the strength of filtering
        new_frame=cv2.erode(new_frame, kernel, iterations=3) #Erodes the image, reducing noise and helping isolate the iris further. The number of iterations (3) controls the strength.
        new_frame=cv2.threshold(new_frame,threshold, 255, cv2.THRESH_BINARY)[1] #Converts the image to binary (black and white) using the given threshold. Pixels above the threshold become white, and those below become black. This helps separate the iris from surrounding areas.

        return new_frame   #Returns the processed frame that ideally highlights the iris as a distinct area.

    def detect_iris(self,eye_frame):
        """ Detects the iris and estimates the position of the iris by
        calculating the centroid.

        Arguments:
            eye_frame(numpy.ndarray): Frame containing an eye and nothing else
        """
        self.iris_frame=self.image_processing(eye_frame, self.threshold)    #Calls image_processing to obtain a binarized version of the eye frame, highlighting the iris

        contours, _= cv2.findContours(self.iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]  #Detects contours in iris_frame, retrieving boundary points that enclose white areas (potential irises)
        contours= sorted(contours, key=cv2.contourArea)  #Sorts contours by area to prioritize the larger regions, assuming the largest one is the iris.

        "cv2.moments() calculates various spatial moments (essentially weighted averages) based on the shape of a contour, which is useful for calculating the center"
        try:
            moments= cv2.moments(contours[-2])  #contours is a list of all detected contours in the iris_frame, ordered by their area. The second-largest contour is often the iris (assuming the largest is the eye boundary)
            self.x=int(moments['m10']/moments['m00'])  # m00: Represents the area of the contour. m10 and m01: Represent spatial moments, helping compute the x and y coordinates of the center (or centroid).
            self.y=int(moments['m01']/moments['m00'])  # This line calculates the y-coordinate of the iris's centroid, similar to the x-coordinate calculation. moments['m01'] is the sum of the y-coordinates of all contour pixels, weighted by intensity.Dividing m01 by m00 gives the y-coordinate of the centroid.
        except (IndexError, ZeroDivisionError):
            pass



