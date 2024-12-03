import math
import numpy as np
import cv2
from .pupil import Pupil

class Eye(object): #This class is responsible for isolating an eye from the image, calculating whether the eye is open or closed, and detecting the pupil’s location.
    """ This class creates a new frame to isolate the eye and initiates the pupil detection."""

    LEFT_EYE_POINTS=[36,37,38,39,40,41]
    RIGHT_EYE_POINTS=[42,43,44,45,46,47]

    def __init__(self, original_frame, landmarks, side, calibration):
        """original_frame: The frame containing the face.
        landmarks: Facial landmark points for the face.
        side: Indicates whether it’s the left (0) or right (1) eye.
        calibration: A Calibration object that manages threshold values for eye calibration"""
        self.frame=None   #Stores the isolated eye frame.
        self.origin=None  #Stores the coordinates of the top-left corner of the isolated eye region
        self.center=None  #Stores the center point of the isolated eye frame.
        self.pupil= None  #Stores a Pupil object.
        self.landmark_points = None  #Stores the landmark points surrounding the eye

        self._analyze(original_frame, landmarks, side, calibration)  # Initializes the eye by calling the _analyze method to isolate the eye and detect the pupil.

    @staticmethod
    def _middle_point(p1,p2):
        """ Returns the middle point (x,y) between two pints

        Arguments:
            p1 (dlib.point) : First point
            p2 (dlib.point) : Second point
        """

        x= int((p1.x + p2.x) / 2)   #Calculates the midpoint between two given points p1 and p2, often used to find the midpoint of the top and bottom of the eye to measure its height.
        y= int((p1.y + p2.y) / 2)
        return (x, y)

    def _isolate(self, frame, landmarks, points):
        """ Isolate an eye, to have a frame without other part of the face.

        Arguments:
            frame(numpy.ndarray): Frame containing the face
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            points (list) : Points of an eye (from the 68 Multi-PIE landmarks)
        """
        #This part extracts the coordinates of the eye region based on landmark points. This data allows us to isolate the eye region precisely within the facial frame.
        region=np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in points]) #This part extracts the coordinates of the eye region based on landmark points. It forms an array region containing (x, y) coordinates for each eye landmark.
        region=region.astype(np.int32) #astype(np.int32) ensures that the array uses integer data, which is needed for OpenCV functions.
        self.landmark_points=region #self.landmark_points stores these points, which can be used later for tracking or drawing.

        # Applying a mask to get only the eye
        height, width = frame.shape[:2] # This line retrieves the dimensions of the input frame, specifically the height and width. frame.shape returns a tuple representing the dimensions of the frame. If the frame is in grayscale, it has two dimensions: (height, width). If it’s in color, it has three: (height, width, channels). frame.shape[:2] extracts only the first two values (height and width), ignoring any color channel information if present.
        black_frame= np.zeros((height, width), np.uint8) #generates an array of zeros with a shape of (height, width). Each pixel has a value of 0, which represents black in grayscale. black_frame is a blank image, completely black and the same size as frame.
        mask=np.full((height, width), 255, np.uint8) #creates a white mask image with the same dimensions as frame.
        cv2.fillPoly(mask, [region], (0,0,0)) # fills the area within the region polygon in the mask image with black (0)
        eye= cv2.bitwise_not(black_frame, frame.copy(), mask=mask) # This line isolates the eye region by combining black_frame and frame using the mask as a guide

        # cropping on the eye
        margin=5 #A small margin helps ensure that when the eye area is cropped, it captures a bit of the surrounding area. This is useful because detection might not be exact, so a margin provides a better capture of the eye.
        #These lines determine the left and right bounds of the cropping area around the eye
        min_x=np.min(region[:,0])- margin # finds the smallest x-coordinate (leftmost point of the eye landmarks).
        max_x=np.max(region[:,0])+ margin # finds the largest x-coordinate (rightmost point of the eye landmarks).

        #These lines determine the top and bottom bounds of the cropping area around the eye.
        min_y = np.min(region[:,1]) - margin # finds the smallest y-coordinate (topmost point of the eye landmarks).
        max_y = np.max(region[:,1]) + margin # finds the largest y-coordinate (bottommost point of the eye landmarks).

        self.frame= eye[min_y:max_y, min_x:max_x] # crops the isolated eye area from the eye image, storing it in self.frame. eye[min_y:max_y, min_x:max_x] selects the region within the calculated min_y, max_y, min_x, and max_x boundaries. This cropping operation extracts only the eye area, along with a slight margin around it. self.frame is assigned this cropped eye image, so self.frame now contains only the eye region.

        self.origin=(min_x, min_y)  # records the top-left corner of the cropped eye area in the original image. Knowing this origin point can be helpful if you need to map the cropped eye area back to its original location in the larger image.

        height, width =self.frame.shape[:2] #  extracts the height and width of the cropped eye frame, stored in self.frame.
        self.center= (width/2, height/2) # width / 2 and height / 2 give the x and y coordinates of the midpoint within the cropped eye area. elf.center stores this midpoint, which represents the center of the cropped eye region.

    def _blinking_ratio(self, landmarks, points):
        """Calculates a ratio that can indicate whether an eye is closed or not.
        It's the division of the width of the eye, by its height.

        Arguments:
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            points (list): Points of an eye (from the 68 Multi-PIE landmarks)

        Returns:
            The computed ratio
        """
        #Defines two points to measure the horizontal distance (width) of the eye.
        left =(landmarks.part(points[0]).x, landmarks.part(points[0]).y) # left is set to the coordinates of the first landmark in points, which is the left corner of the eye.
        right=(landmarks.part(points[3]).x, landmarks.part(points[3]).y) # right is set to the coordinates of the fourth landmark in points, which is the right corner of the eye. now have the (x, y) coordinates for the left and right corners of the eye, which will help us calculate the eye’s width.

        #Defines two points to measure the vertical distance (height) of the eye.
        top= self._middle_point(landmarks.part(points[1]), landmarks.part(points[2])) # top is calculated as the midpoint between the landmarks at indices points[1] and points[2]. These landmarks define the top portion of the eye.
        bottom = self._middle_point(landmarks.part(points[5]), landmarks.part(points[4])) # bottom is calculated as the midpoint between the landmarks at indices points[5] and points[4], defining the bottom of the eye.

        #math.hypot(x, y) computes the Euclidean distance: sqrt(x^2+y^2)
        eye_width = math.hypot((left[0] - right[0]), (left[1] - right[1])) # left[0] - right[0] gives the x-axis distance between left and right. left[1] - right[1] gives the y-axis distance between left and right.
        eye_height = math.hypot((top[0] - bottom[0]), (top[1] - bottom[1]))

        try:
            ratio= eye_width / eye_height #ratio = eye_width / eye_height gives a ratio that indicates how "open" the eye is.
        except ZeroDivisionError : # If eye_height is zero (which would cause division by zero), the code catches this error and sets ratio to None to avoid a crash.
            ratio= None

        return ratio

    def _analyze(self, original_frame, landmarks, side, calibration):
        """Detects and isolates the eye in a new frame, sends data to the calibration
         and initializes Pupil object.

        Arguments:
            original_frame (numpy.ndarray): Frame passed by the user
            landmarks (dlib.full_object_detection): Facial landmarks for the face region
            side: Indicates whether it's the left eye (0) or the right eye (1)
            calibration (calibration.Calibration): Manages the binarization threshold value
        """
        # Determine which set of points to use based on the side argument.
        if side ==0:
            points= self.LEFT_EYE_POINTS   #If side is 0, this is the left eye, so points is set to self.LEFT_EYE_POINTS, which is a predefined list of points around the left eye.
        elif side ==1:
            points =self.RIGHT_EYE_POINTS  # If side is 1, this is the right eye, so points is set to self.RIGHT_EYE_POINTS.
        else:
            return   # If side is neither 0 nor 1, it returns immediately without doing anything.

        self.blinking = self._blinking_ratio(landmarks, points)  # calculated ratio is stored in self.blinking and will help track whether the eye is open or closed
        self._isolate(original_frame, landmarks, points) # The result is stored in self.frame, the isolated eye frame, and self.origin, which records the top-left coordinates of the eye in the original frame.

        if not calibration.is_complete():  # calibration.is_complete() checks if the calibration is already finished. If not, it evaluates the current eye frame to fine-tune the threshold settings.
            calibration.evaluate(self.frame, side) # calibration.evaluate(self.frame, side) analyzes the isolated eye frame to help determine the optimal threshold for binarizing the pupil area.

        threshold= calibration.threshold(side)   # calibration.threshold(side) retrieves the threshold value based on the eye’s side (left or right), which helps isolate the pupil area in the next step.
        self.pupil= Pupil(self.frame, threshold)  # The Pupil class is initialized with self.frame (the isolated eye image) and the threshold. This object will detect the pupil position, storing it in self.pupil.



