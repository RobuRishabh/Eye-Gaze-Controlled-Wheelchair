
# Eye-Gaze Controlled Wheelchair

## Project Overview

This project focuses on developing an affordable and user-friendly **eye-gaze controlled wheelchair** to restore mobility and independence for patients suffering from ALS. The system utilizes gaze tracking technology to interpret eye movements and translate them into wheelchair navigation commands.

## Features
- **Gaze Tracking**: Tracks eye movement using a monocular camera.
- **Eye Detection**: Detects and isolates eye regions using Dlib and OpenCV.
- **Pupil Detection**: Determines pupil positions for gaze direction analysis.
- **Wheelchair Control Interface**: Commands include stop, turn left, turn right, and move straight.
- **Wireless Communication**: Supports real-time data transfer using ESP8266 and Arduino.

## Components
- **Hardware**: Camera, Arduino, motorized wheelchair emulator, ESP8266.
- **Software**: Python, OpenCV, Dlib, and custom modules for calibration and gaze tracking.

## How It Works
1. **Eye Tracking**:
   - Detects facial landmarks and isolates eye regions.
   - Tracks pupil positions to determine gaze direction.
2. **Gaze-Based Navigation**:
   - Double blink to engage the system.
   - Single blink to stop.
   - Look left, right, or forward for directional movement.
3. **Control Signals**:
   - Eye movements are processed into actionable commands via Arduino.
   - Commands are sent wirelessly to the wheelchair emulator.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/RobuRishabh/Eye-Gaze-Controlled-Wheelchair.git
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Place the `shape_predictor_68_face_landmarks.dat` file in the `trained_models` directory. You can download this file from her 
   ```
   https://huggingface.co/public-data/dlib_face_landmark_model/blob/main/shape_predictor_68_face_landmarks.dat
   ```

## Usage
1. Run the gaze tracking system:
   ```bash
   python main.py
   ```
2. Follow on-screen instructions for calibration and navigation.

## Future Scope
- Integrating advanced camera systems for better accuracy.
- Adding path planning and obstacle detection features.
- Optimizing control algorithms for smoother operation.

## Acknowledgments
Special thanks to our professor **Dr. Bazzi Salah** for his guidance and support throughout the project.

