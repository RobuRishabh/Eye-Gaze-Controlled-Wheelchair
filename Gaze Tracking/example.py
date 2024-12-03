"""
Integration of GazeTracking with Arduino for robot control.
"""

import cv2
import serial
import time
from gaze_tracking.gaze_tracking import GazeTracking

# Initialize GazeTracking
gaze = GazeTracking()
webcam = cv2.VideoCapture(1)

# Set the resolution to 720p
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Initialize serial communication with Arduino
arduino = serial.Serial('COM3', 9600, timeout=1)  # Replace 'COM3' with your Arduino's COM port
time.sleep(2)  # Allow time for Arduino to reset

# Set frequency to 10 Hz (0.1 seconds per cycle)
frequency = 0.5

while True:
    start_time = time.time()  # Start time for frequency control
    
    _, frame = webcam.read()
    gaze.refresh(frame)
    frame = gaze.annotated_frame()
    command = ""

    # Determine gaze direction and corresponding command
    # if gaze.is_blinking():
    #     command = "B"  # Stop
    # elif gaze.is_right():
    #     command = "R20"  # Move right
    # elif gaze.is_left():
    #     command = "L20"  # Move left
    # elif gaze.is_center():
    #     command = "D50"  # Move forward
    if gaze.is_blinking():
        command = "STOP"
    elif gaze.is_right():
        command = "RIGHT"
    elif gaze.is_left():
        command = "LEFT"
    elif gaze.is_center():
        command = "CENTER"

    # Send command to Arduino as a string
    if command:
        arduino.write((command + "\n").encode('ascii'))  # Send with newline for easier parsing on Arduino
        print(f"Sent command: {command}")

    # Display the command on the frame
    cv2.putText(frame, command, (100, 100), cv2.FONT_HERSHEY_DUPLEX, 1.6, (0, 0, 255), 2)
    cv2.imshow("Demo", frame)

    # Wait to maintain the frequency
    elapsed_time = time.time() - start_time
    if elapsed_time < frequency:
        time.sleep(frequency - elapsed_time)

    if cv2.waitKey(1) == 27:  # Exit on pressing 'Esc'
        break

webcam.release()
cv2.destroyAllWindows()
arduino.close()