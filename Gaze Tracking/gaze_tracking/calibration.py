from __future__ import division
import cv2
from .pupil import Pupil

class Calibration(object):   #accurately detect the pupil in an eye frame
    """
    This class calibrate the pupil detection algorithm by finding the
    best binarization threshold value for the person and webcam.
    """

    def __init__(self):
        self.nb_frames=20  #Specifies the required number of frames (20) to complete calibration.
        self.thresholds_left=[]  #These lists store the binarization threshold values computed for the left and right eyes over multiple frames.
        self.thresholds_right=[]

    def is_complete(self):    # Checks if calibration is complete, which happens when both eyes have enough threshold values (20 frames each).
        """ Returns true if the calibration is completed"""
        return len(self.thresholds_left) >= self.nb_frames and len(self.thresholds_right)>= self.nb_frames

    def threshold(self, side):   #Computes the average threshold for the specified eye.
        """ Returns the threshold value for the given eye.

        Arguments:
            side: Indicates whether it's the left eye(0) or the right eye(1)
        """
        if side == 0:
            return int(sum(self.thresholds_left)/ len(self.thresholds_left))
        elif side == 1:
            return int(sum(self.thresholds_right)/ len(self.thresholds_right))

    @staticmethod
    def iris_size(frame):   #Calculates the percentage of black (pupil) pixels in an eye frame to determine the size of the iris.
        """ returns the percentage of space that the iris takes up on the surface of the eye.
        Argument:
            frame (numpy.ndarray) : Binarized iris frame
        """
        frame= frame[5:-5, 5:-5]    # Crops 5 pixels off each side to remove noise at the edges.
        height, width =frame.shape[:2]   #Retrieves frame dimensions.
        nb_pixels = height * width   #Calculates the total number of pixels in the cropped frame.
        nb_blacks = nb_pixels - cv2.countNonZero(frame) #Counts black pixels in the frame by subtracting non-zero pixels from the total.
        return nb_blacks / nb_pixels   #The ratio of black pixels to total pixels, indicating the percentage of the frame covered by the iris.

    @staticmethod
    def find_best_threshold(eye_frame):   #Determines the threshold that produces the most accurate iris size.
        """ Calculate the optimal threshold to binarize the frame for the given eye.
        Argument:
            eye_frame(numpy.ndarray): Frame of the eye to analyzed
        """
        average_iris_size=0.48   #Expected percentage of the eye covered by the iris.
        trials ={}    #Dictionary to store threshold values as keys and iris sizes as values.

        for threshold in range (5,100,5):  #Iterates over possible threshold values (5 to 95).
            iris_frame = Pupil.image_processing(eye_frame, threshold) #Binarizes the eye frame using Pupil.image_processing at the current threshold
            trials[threshold]= Calibration.iris_size(iris_frame) # Stores the iris size computed at this threshold.

        best_threshold, iris_size = min(trials.items(), key=(lambda p: abs(p[1] - average_iris_size)))  #trials is a dictionary where each key is a threshold value (e.g., 5, 10, 15, etc.), and each corresponding value is the measured iris size when that threshold was applied.Calling trials.items() returns a list of key-value pairs (tuples) in the formmin() is a function that returns the smallest item in an iterable (in this case, the dictionary items).The key parameter in min() allows us to define a custom rule for determining the "smallest" item.p[1] accesses the iris_size in each tuple.This difference (abs(p[1] - average_iris_size)) is used as the "weight" for each item when min() evaluates it.
        return best_threshold

    def evaluate(self, eye_frame, side):
        """ Improves calibration by taking into consideration the given image.

        Arguments:
            eye_frame(numpy.ndarray): Frame of the eye
            side: Indicates whether it's the left eye (0) or the right eye (1)
        """
        threshold =self.find_best_threshold(eye_frame)

        if side==0:
            self.thresholds_left.append(threshold)    #self.thresholds_left is a list of threshold values that have been calculated for the left eye.
        elif side==1:
            self.thresholds_right.append(threshold)

        #The evaluate function improves calibration by calculating an optimal threshold for binarizing the eye frame and storing this threshold in either thresholds_left (for the left eye) or thresholds_right (for the right eye). As more frames are evaluated, these lists accumulate values, which will help average or determine a final threshold for each eye, aiding in consistent pupil detection.

