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

# Set frequency to 0.5 seconds (2 Hz)
frequency = 0.5

# Variables for blink counting and movement control
blink_count = 0
movement_allowed = False

while True:
    start_time = time.time()  # Start time for frequency control

    _, frame = webcam.read()
    gaze.refresh(frame)
    frame = gaze.annotated_frame()
    command = ""

    # Check for blinking and increment blink count
    if gaze.is_blinking():
        if blink_count < 3:  # Allow up to 3 blinks to be counted
            blink_count += 1
            print(f"Blink count: {blink_count}")

            time.sleep(0.9)  # Add a short delay to avoid counting the same blink multiple times

    if blink_count == 1:  # Stop robot if blink count is 1 or eyes are shut
        command = "STOP"
        movement_allowed = False
    elif blink_count in [2, 3]:  # Allow movement after two or three blinks
        movement_allowed = True
        blink_count = 0  # Reset blink count after movement is allowed

    # Determine movement command based on gaze direction
    if movement_allowed:
        if gaze.is_right():
            command = "RIGHT"  # Turn right
        elif gaze.is_left():
            command = "LEFT"  # Turn left
        elif gaze.is_center():
            command = "CENTER"  # Move forward
    else:
        command = "STOP"  # If movement is not allowed, stop the robot

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
